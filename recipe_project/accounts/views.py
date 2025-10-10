from django.shortcuts import render, redirect
from django.contrib.auth import login, views as auth_views, get_user_model
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator

from .forms import CustomUserCreationForm, ProfileEditForm
from .models import CustomUser

User = get_user_model()


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            current_site = request.get_host()
            subject = 'Активация аккаунта на RecipeBook'

            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            context = {
                'user': user,
                'domain': current_site,
                'uid': uid,
                'token': token,
            }
            email_message = render_to_string('accounts/account_activation_email.html', context)

            send_mail(
                subject,
                email_message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                html_message=email_message,
                fail_silently=False,
            )

            messages.info(request, 'Аккаунт успешно создан! Для входа проверьте Email и активируйте его.')
            return redirect('login')
        else:
            messages.error(request, 'Ошибка регистрации. Проверьте введенные данные.')

    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if user.is_active:
            messages.warning(request, 'Ваш аккаунт уже был активирован.')
            return redirect('login')

        user.is_active = True
        user.save()
        login(request, user)
        messages.success(request, '🎉 Ваш аккаунт успешно активирован! Теперь вы можете пользоваться всеми функциями.')
        return redirect('recipe_list')
    else:
        messages.error(request, 'Ссылка активации недействительна или просрочена.')
        return redirect('register')


@login_required
def resend_activation_email(request):
    if request.user.is_active:
        messages.warning(request, 'Ваш аккаунт уже активен.')
        return redirect('profile')

    user = request.user
    current_site = request.get_host()
    subject = 'Повторная активация аккаунта на RecipeBook'

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    context = {
        'user': user,
        'domain': current_site,
        'uid': uid,
        'token': token,
    }
    email_message = render_to_string('accounts/account_activation_email.html', context)

    send_mail(
        subject,
        email_message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=email_message,
        fail_silently=False,
    )

    messages.success(request, f'Письмо для активации отправлено повторно на {user.email}.')
    return redirect('recipe_list')


@login_required
def profile(request):
    try:
        Recipe = request.user.recipe_set.model
        user_recipes = Recipe.objects.filter(author=request.user).order_by('-created_at')
    except AttributeError:
        user_recipes = []

    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user = form.save(commit=False)

            if user.unconfirmed_email:
                user.save()

                new_email = user.unconfirmed_email
                current_site = request.get_host()
                subject = 'Подтверждение смены Email на RecipeBook'

                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)

                context = {
                    'user': user,
                    'domain': current_site,
                    'uid': uid,
                    'token': token,
                    'new_email': new_email,
                }
                email_message = render_to_string('accounts/email_change_email.html', context)

                send_mail(
                    subject,
                    email_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [new_email],
                    html_message=email_message,
                    fail_silently=False,
                )

                messages.info(request,
                              f'На новый адрес {new_email} отправлено письмо для подтверждения. Email будет изменен только после активации.')
                return redirect('profile')

            else:
                user.save()
                messages.success(request, 'Профиль успешно обновлен!')
                return redirect('profile')
        else:
            messages.error(request, 'Ошибка при обновлении профиля. Проверьте введенные данные.')
    else:
        form = ProfileEditForm(instance=request.user)

    return render(request, 'accounts/profile.html', {
        'user_recipes': user_recipes,
        'profile_form': form,
    })


def confirm_email_change(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user is None or not user.unconfirmed_email:
        messages.error(request, 'Ссылка подтверждения недействительна.')
        return redirect('profile')

    if user is not None and default_token_generator.check_token(user, token):
        user.email = user.unconfirmed_email
        user.unconfirmed_email = None
        user.save()

        messages.success(request, f'Ваш Email успешно изменен на {user.email}.')
        return redirect('profile')
    else:
        messages.error(request, 'Ссылка подтверждения недействительна или просрочена.')
        return redirect('profile')


@login_required
def resend_email_change_email(request):
    if not request.user.unconfirmed_email:
        messages.error(request, 'У вас нет неподтвержденного запроса на смену Email.')
        return redirect('profile')

    user = request.user
    new_email = user.unconfirmed_email

    current_site = request.get_host()
    subject = 'Повторное подтверждение смены Email на RecipeBook'

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    context = {
        'user': user,
        'domain': current_site,
        'uid': uid,
        'token': token,
        'new_email': new_email,
    }
    email_message = render_to_string('accounts/email_change_email.html', context)

    send_mail(
        subject,
        email_message,
        settings.DEFAULT_FROM_EMAIL,
        [new_email],
        html_message=email_message,
        fail_silently=False,
    )

    messages.success(request, f'Письмо для подтверждения смены Email отправлено повторно на {new_email}.')
    return redirect('profile')


class CustomPasswordResetView(auth_views.PasswordResetView):
    template_name = 'accounts/password_reset_form.html'
    email_template_name = 'accounts/password_reset_email.html'
    subject_template_name = 'accounts/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')

    def form_valid(self, form):
        email = form.cleaned_data['email']
        try:
            User.objects.get(email__iexact=email, is_active=True)
        except User.DoesNotExist:
            messages.error(self.request, 'Аккаунт с таким Email не зарегистрирован или не активирован.')
            return self.render_to_response(self.get_context_data(form=form))
        return super().form_valid(form)


class PasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'accounts/password_reset_done.html'


class PasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')


class PasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'accounts/password_reset_complete.html'