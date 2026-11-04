import { provideHttpClient } from '@angular/common/http';
import {
  HttpTestingController,
  provideHttpClientTesting,
} from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { InventoryService } from './inventory.service';

describe('InventoryService', () => {
  let service: InventoryService;
  let http: HttpTestingController;

  const item = {
    id: 10,
    codigo_patrimonio: 'PAT-10',
    descricao: 'Notebook',
    estado_conservacao: 'Bom',
    situacao: 'Ativo',
    data_aquisicao: null,
    valor: null,
    setor: 2,
    setor_nome: 'Informática',
    tipo_bem: 1,
    tipo_bem_nome: 'Equipamento',
  };

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
    service = TestBed.inject(InventoryService);
    http = TestBed.inject(HttpTestingController);
  });

  afterEach(() => http.verify());

  it('loads the inventory and catalogs from the unified API', async () => {
    const inventoryRequest = service.list();
    http.expectOne('/bens/').flush({ results: [item] });
    await expect(inventoryRequest).resolves.toEqual([item]);

    const typesRequest = service.listTiposBem();
    http.expectOne('/tipos_bem/').flush([{ id: 1, nome: 'Equipamento', descricao: null }]);
    await expect(typesRequest).resolves.toEqual([
      { id: 1, nome: 'Equipamento', descricao: null },
    ]);

    const sectorsRequest = service.listSetores();
    http.expectOne('/setores/').flush([{ id: 2, nome: 'Informática', descricao: null }]);
    await expect(sectorsRequest).resolves.toEqual([
      { id: 2, nome: 'Informática', descricao: null },
    ]);
  });

  it('uses the unified inventory endpoint for create, update and delete', async () => {
    const payload = {
      codigo_patrimonio: item.codigo_patrimonio,
      descricao: item.descricao,
      estado_conservacao: item.estado_conservacao,
      situacao: item.situacao,
      data_aquisicao: item.data_aquisicao,
      valor: item.valor,
      setor: item.setor,
      tipo_bem: item.tipo_bem,
    };

    const createRequest = service.create(payload);
    const createHttp = http.expectOne('/bens/');
    expect(createHttp.request.method).toBe('POST');
    createHttp.flush(item);
    await expect(createRequest).resolves.toEqual(item);

    const updateRequest = service.update(item.id, payload);
    const updateHttp = http.expectOne('/bens/10/');
    expect(updateHttp.request.method).toBe('PUT');
    updateHttp.flush(item);
    await expect(updateRequest).resolves.toEqual(item);

    const deleteRequest = service.delete(item.id);
    const deleteHttp = http.expectOne('/bens/10/');
    expect(deleteHttp.request.method).toBe('DELETE');
    deleteHttp.flush(null);
    await expect(deleteRequest).resolves.toBeUndefined();
  });
});
