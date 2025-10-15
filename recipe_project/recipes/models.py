from django.db import models
from django.conf import settings


class Category(models.Model):
    name = models.CharField(max_length=50, verbose_name="Категория")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name


class Recipe(models.Model):
    title = models.CharField(max_length=100, verbose_name="Название рецепта")
    description = models.TextField(verbose_name="Описание")
    ingredients = models.TextField(verbose_name="Ингредиенты")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, verbose_name="Категория")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Автор")
    image = models.ImageField(upload_to='recipes/', blank=True, null=True, verbose_name="Изображение (опционально)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return self.title


class Step(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='steps',
        verbose_name="Рецепт"
    )
    step_number = models.PositiveIntegerField(default=1, verbose_name="Номер шага")
    instruction = models.TextField(verbose_name="Инструкция")
    image = models.ImageField(
        upload_to='recipe_steps/',
        blank=True,
        null=True,
        verbose_name="Изображение (опционально)"
    )

    class Meta:
        ordering = ['step_number']
        verbose_name = "Шаг"
        verbose_name_plural = "Шаги"

    def __str__(self):
        return f'Шаг {self.step_number} для {self.recipe.title}'


class Comment(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='comments', verbose_name="Рецепт")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Пользователь")
    text = models.TextField(verbose_name="Комментарий")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"

    def __str__(self):
        return f'{self.user.username} - {self.recipe.title}'
