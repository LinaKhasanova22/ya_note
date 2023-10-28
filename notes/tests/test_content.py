from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()

NOTES_COUNT_ON_LIST_PAGE = 10


class TestListPage(TestCase):
    LIST_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметки')
        cls.guest = User.objects.create(username='Посетитель')
        Note.objects.bulk_create(
            Note(
                title=f'Заметка {index}',
                author=cls.author,
                text=f'Текст {index}',
                slug=f'slug{index}'
            )
            for index in range(NOTES_COUNT_ON_LIST_PAGE)
        )

    def test_notes_in_list(self):
        self.client.force_login(self.author)
        response = self.client.get(self.LIST_URL)
        object_list = response.context['object_list']
        notes_count = len(object_list)
        self.assertEqual(notes_count, NOTES_COUNT_ON_LIST_PAGE)


class TestFormPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметки')
        cls.notes = Note.objects.create(
            title='Заметка',
            text='Просто текст.',
            slug='slug',
            author=cls.author,
        )
        cls.add_url = reverse('notes:add')
        cls.edit_url = reverse('notes:edit', args=(cls.notes.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.notes.slug,))

    def test_authorized_client_has_form(self):
        self.client.force_login(self.author)
        for url in (self.add_url, self.edit_url):
            response = self.client.get(url)
            self.assertIn('form', response.context)
