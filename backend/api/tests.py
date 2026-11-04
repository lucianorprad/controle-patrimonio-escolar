import json

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from rest_framework.test import APITestCase

from .models import Bem, Localizacao, Movimentacao, Setor, TipoBem


class PatrimonioApiTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="test-password",
        )
        self.client.force_authenticate(user=self.user)
        self.tipo_bem = TipoBem.objects.create(nome="Equipamento")
        self.setor = Setor.objects.create(nome="Informática")

    def test_create_bem_uses_diagram_fields(self):
        response = self.client.post(
            "/bens/",
            {
                "codigo_patrimonio": "PAT-1000",
                "descricao": "Notebook",
                "estado_conservacao": "Bom",
                "situacao": "Ativo",
                "setor": self.setor.pk,
                "tipo_bem": self.tipo_bem.pk,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["codigo_patrimonio"], "PAT-1000")
        self.assertEqual(response.data["setor_nome"], "Informática")
        self.assertEqual(response.data["tipo_bem_nome"], "Equipamento")
        self.assertTrue(Bem.objects.filter(codigo_patrimonio="PAT-1000").exists())

    def test_update_and_delete_bem(self):
        bem = Bem.objects.create(
            codigo_patrimonio="PAT-1001",
            descricao="Notebook antigo",
            estado_conservacao=Bem.EstadoConservacao.REGULAR,
            situacao=Bem.Situacao.ATIVO,
            setor=self.setor,
            tipo_bem=self.tipo_bem,
        )
        response = self.client.patch(
            f"/bens/{bem.pk}/",
            {"descricao": "Notebook atualizado"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        bem.refresh_from_db()
        self.assertEqual(bem.descricao, "Notebook atualizado")

        response = self.client.delete(f"/bens/{bem.pk}/")

        self.assertEqual(response.status_code, 204)
        self.assertFalse(Bem.objects.filter(pk=bem.pk).exists())

    def test_movement_uses_diagram_relations(self):
        bem = Bem.objects.create(
            codigo_patrimonio="PAT-1002",
            descricao="Projetor",
            estado_conservacao=Bem.EstadoConservacao.BOM,
            situacao=Bem.Situacao.ATIVO,
            setor=self.setor,
            tipo_bem=self.tipo_bem,
        )
        origem = Localizacao.objects.create(nome="Sala 1")
        destino = Localizacao.objects.create(nome="Sala 2")
        response = self.client.post(
            "/movimentacoes/",
            {
                "data_movimentacao": "2026-11-02T18:00:00Z",
                "setor": self.setor.pk,
                "localizacao_origem": origem.pk,
                "localizacao_destino": destino.pk,
                "bem": bem.pk,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["localizacao_origem_nome"], "Sala 1")
        self.assertEqual(response.data["localizacao_destino_nome"], "Sala 2")
        self.assertTrue(Movimentacao.objects.filter(bem=bem).exists())

    def test_regular_user_cannot_write_inventory_or_manage_users(self):
        user = get_user_model().objects.create_user(
            username="visitante",
            email="visitante@example.com",
            password="test-password",
        )
        self.client.force_authenticate(user=user)

        inventory_response = self.client.post(
            "/bens/",
            {
                "codigo_patrimonio": "PAT-1003",
                "descricao": "Projetor",
                "estado_conservacao": "Bom",
                "situacao": "Ativo",
                "setor": self.setor.pk,
                "tipo_bem": self.tipo_bem.pk,
            },
            format="json",
        )
        users_response = self.client.get("/users/")
        groups_response = self.client.get("/groups/")

        self.assertEqual(inventory_response.status_code, 403)
        self.assertEqual(users_response.status_code, 403)
        self.assertEqual(groups_response.status_code, 403)


class AllauthBrowserLoginTests(TestCase):
    def test_browser_login_session_and_logout(self):
        get_user_model().objects.create_user(
            username="login-user",
            email="login@example.com",
            password="test-password",
        )
        client = Client(enforce_csrf_checks=True)

        config_response = client.get("/_allauth/browser/v1/config")
        self.assertEqual(config_response.status_code, 200)
        self.assertIn("csrftoken", client.cookies)

        login_response = client.post(
            "/_allauth/browser/v1/auth/login",
            data=json.dumps({"username": "login-user", "password": "test-password"}),
            content_type="application/json",
            HTTP_X_CSRFTOKEN=client.cookies["csrftoken"].value,
        )
        self.assertEqual(login_response.status_code, 200)
        self.assertTrue(login_response.json()["meta"]["is_authenticated"])

        session_response = client.get("/_allauth/browser/v1/auth/session")
        self.assertTrue(session_response.json()["meta"]["is_authenticated"])

        logout_response = client.delete(
            "/_allauth/browser/v1/auth/session",
            HTTP_X_CSRFTOKEN=client.cookies["csrftoken"].value,
        )
        self.assertEqual(logout_response.status_code, 401)
        self.assertFalse(logout_response.json()["meta"]["is_authenticated"])
