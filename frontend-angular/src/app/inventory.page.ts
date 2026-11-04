import { CommonModule } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import { Component, OnInit, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from './auth.service';
import {
  CatalogItem,
  InventoryItem,
  InventoryPayload,
  InventoryService,
} from './inventory.service';

type InventoryFilter = number | 'all';

interface InventoryForm {
  codigo_patrimonio: string;
  descricao: string;
  estado_conservacao: string;
  situacao: string;
  data_aquisicao: string;
  valor: number | null;
  setor: number | null;
  tipo_bem: number | null;
}

const EMPTY_FORM: InventoryForm = {
  codigo_patrimonio: '',
  descricao: '',
  estado_conservacao: 'Bom',
  situacao: 'Ativo',
  data_aquisicao: '',
  valor: null,
  setor: null,
  tipo_bem: null,
};

@Component({
  selector: 'app-inventory-page',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './inventory.page.html',
  styleUrl: './inventory.page.css',
})
export class InventoryPage implements OnInit {
  private readonly inventoryService = inject(InventoryService);
  private readonly authService = inject(AuthService);
  private readonly router = inject(Router);
  private listRequestId = 0;

  readonly estadosConservacao = ['Ótimo', 'Bom', 'Regular', 'Ruim'];
  readonly situacoes = ['Ativo', 'Baixado'];

  tiposBem: CatalogItem[] = [];
  setores: CatalogItem[] = [];
  listFilter: InventoryFilter = 'all';
  form: InventoryForm = { ...EMPTY_FORM };
  items: InventoryItem[] = [];
  editingId: number | null = null;
  isLoading = false;
  isLoadingCatalogs = false;
  isSaving = false;
  isSigningOut = false;
  mensagem = '';
  isError = false;

  ngOnInit(): void {
    void this.loadCatalogs();
    void this.loadItems();
  }

  get visibleItems(): InventoryItem[] {
    return this.listFilter === 'all'
      ? this.items
      : this.items.filter((item) => item.tipo_bem === this.listFilter);
  }

  get listTitle(): string {
    if (this.listFilter === 'all') {
      return 'Todos os bens';
    }
    return this.tiposBem.find((tipo) => tipo.id === this.listFilter)?.nome ?? 'Inventário';
  }

  async loadCatalogs(): Promise<void> {
    this.isLoadingCatalogs = true;
    try {
      const [tiposBem, setores] = await Promise.all([
        this.inventoryService.listTiposBem(),
        this.inventoryService.listSetores(),
      ]);
      this.tiposBem = tiposBem;
      this.setores = setores;
    } catch (error) {
      this.showError(error, 'Não foi possível carregar os tipos de bem e setores.');
    } finally {
      this.isLoadingCatalogs = false;
    }
  }

  async loadItems(): Promise<void> {
    this.mensagem = '';
    const requestId = ++this.listRequestId;
    this.isLoading = true;
    try {
      const items = await this.inventoryService.list();
      if (requestId === this.listRequestId) {
        this.items = items;
      }
    } catch (error) {
      if (requestId === this.listRequestId) {
        this.showError(error, 'Não foi possível carregar os patrimônios.');
      }
    } finally {
      if (requestId === this.listRequestId) {
        this.isLoading = false;
      }
    }
  }

  async save(): Promise<void> {
    if (this.form.setor === null || this.form.tipo_bem === null) {
      this.mensagem = 'Cadastre e selecione um tipo de bem e um setor.';
      this.isError = true;
      return;
    }

    this.isSaving = true;
    this.mensagem = '';
    const payload = this.toPayload(this.form.setor, this.form.tipo_bem);
    try {
      if (this.editingId === null) {
        await this.inventoryService.create(payload);
        this.mensagem = 'Patrimônio cadastrado.';
      } else {
        await this.inventoryService.update(this.editingId, payload);
        this.mensagem = 'Patrimônio atualizado.';
      }
      this.isError = false;
      this.cancelEdit();
      await this.loadItems();
    } catch (error) {
      this.showError(error, 'Não foi possível salvar o patrimônio.');
    } finally {
      this.isSaving = false;
    }
  }

  edit(item: InventoryItem): void {
    this.editingId = item.id;
    this.form = {
      codigo_patrimonio: item.codigo_patrimonio,
      descricao: item.descricao,
      estado_conservacao: item.estado_conservacao,
      situacao: item.situacao,
      data_aquisicao: item.data_aquisicao ?? '',
      valor: item.valor === null ? null : Number(item.valor),
      setor: item.setor,
      tipo_bem: item.tipo_bem,
    };
    this.mensagem = '';
    this.isError = false;
  }

  async remove(item: InventoryItem): Promise<void> {
    if (!window.confirm(`Excluir o patrimônio ${item.codigo_patrimonio}?`)) {
      return;
    }

    this.mensagem = '';
    try {
      await this.inventoryService.delete(item.id);
      this.items = this.items.filter((current) => current.id !== item.id);
      this.mensagem = 'Patrimônio excluído.';
      this.isError = false;
    } catch (error) {
      this.showError(error, 'Não foi possível excluir o patrimônio.');
    }
  }

  cancelEdit(): void {
    this.editingId = null;
    this.form = { ...EMPTY_FORM };
  }

  async signOut(): Promise<void> {
    this.isSigningOut = true;
    this.mensagem = '';
    try {
      await this.authService.logout();
      await this.router.navigateByUrl('/login');
    } catch (error) {
      this.showError(error, 'Não foi possível encerrar a sessão.');
    } finally {
      this.isSigningOut = false;
    }
  }

  private toPayload(setor: number, tipoBem: number): InventoryPayload {
    return {
      codigo_patrimonio: this.form.codigo_patrimonio.trim(),
      descricao: this.form.descricao.trim(),
      estado_conservacao: this.form.estado_conservacao,
      situacao: this.form.situacao,
      data_aquisicao: this.form.data_aquisicao || null,
      valor: this.form.valor === null ? null : this.form.valor.toFixed(2),
      setor,
      tipo_bem: tipoBem,
    };
  }

  private showError(error: unknown, fallback: string): void {
    this.isError = true;
    if (error instanceof HttpErrorResponse && error.status === 401) {
      this.mensagem = 'Sua sessão expirou. Entre novamente.';
      void this.router.navigateByUrl('/login');
    } else if (error instanceof HttpErrorResponse && error.status === 403) {
      this.mensagem =
        'Sua conta não tem permissão para esta ação. Peça acesso a um administrador.';
    } else if (error instanceof HttpErrorResponse && error.status === 400) {
      this.mensagem = 'Confira os campos informados e tente novamente.';
    } else if (error instanceof HttpErrorResponse && error.status === 0) {
      this.mensagem = 'Não foi possível conectar ao servidor.';
    } else {
      this.mensagem = fallback;
    }
  }
}
