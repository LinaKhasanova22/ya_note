from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметки')
        cls.notes = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author,
            slug='slug'
        )
        cls.url = reverse('notes:detail', args=(cls.notes.slug,))
        cls.form_data = {'text': cls.notes.text}

    def test_user_can_create_note(self):
        self.client.force_login(self.author)
        self.client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note = Note.objects.get()
        self.assertEqual(note.text, self.notes.text)
        self.assertEqual(note.title, self.notes.title)
        self.assertEqual(note.slug, self.notes.slug)
        self.assertEqual(note.author, self.notes.author)

    def slug_is_unique(self):
        self.client.force_login(self.author)
        not_unique_slug = {
            'slug': 'abc',
            'slug': 'abc',
        }
        response = self.client.post(self.url, data=not_unique_slug)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=WARNING
        )
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)


class TestNoteEditDelete(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметки')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.notes = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            author=cls.author,
            slug='slug'
        )
        cls.success_url = reverse('notes:success')
        cls.edit_url = reverse('notes:edit', args=(cls.notes.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.notes.slug,))
        cls.form_data = {'title': 'new_title',
                         'text': 'new_text',
                         'slug': 'new_slug'}

    def test_author_can_delete_note(self):
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.success_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_author_can_edit_note(self):
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.notes.refresh_from_db()
        self.assertRedirects(response, self.success_url)
        self.assertEqual(self.notes.text, self.form_data['text'])
