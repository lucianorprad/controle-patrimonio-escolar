import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { firstValueFrom } from 'rxjs';

export interface CatalogItem {
  id: number;
  nome: string;
  descricao: string | null;
}

export interface InventoryItem {
  id: number;
  codigo_patrimonio: string;
  descricao: string;
  estado_conservacao: string;
  situacao: string;
  data_aquisicao: string | null;
  valor: string | null;
  setor: number;
  setor_nome: string;
  tipo_bem: number;
  tipo_bem_nome: string;
}

export interface InventoryPayload {
  codigo_patrimonio: string;
  descricao: string;
  estado_conservacao: string;
  situacao: string;
  data_aquisicao: string | null;
  valor: string | null;
  setor: number;
  tipo_bem: number;
}

type ListResponse<T> = T[] | { results: T[] };

function unwrapList<T>(response: ListResponse<T>): T[] {
  return Array.isArray(response) ? response : response.results;
}

@Injectable({ providedIn: 'root' })
export class InventoryService {
  private readonly http = inject(HttpClient);

  async list(): Promise<InventoryItem[]> {
    const response = await firstValueFrom(
      this.http.get<ListResponse<InventoryItem>>('/bens/'),
    );
    return unwrapList(response);
  }

  async listTiposBem(): Promise<CatalogItem[]> {
    const response = await firstValueFrom(
      this.http.get<ListResponse<CatalogItem>>('/tipos_bem/'),
    );
    return unwrapList(response);
  }

  async listSetores(): Promise<CatalogItem[]> {
    const response = await firstValueFrom(
      this.http.get<ListResponse<CatalogItem>>('/setores/'),
    );
    return unwrapList(response);
  }

  async create(payload: InventoryPayload): Promise<InventoryItem> {
    return firstValueFrom(this.http.post<InventoryItem>('/bens/', payload));
  }

  async update(id: number, payload: InventoryPayload): Promise<InventoryItem> {
    return firstValueFrom(this.http.put<InventoryItem>(`/bens/${id}/`, payload));
  }

  async delete(id: number): Promise<void> {
    await firstValueFrom(this.http.delete<void>(`/bens/${id}/`));
  }
}
