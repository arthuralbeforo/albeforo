# Order & Pay — Placa QR para impressão 3D (Trem de Minas)

Arquivo CAD multicor da placa **"Order & Pay"** com QR code **funcional**, pronto
para impressão 3D em impressora com troca de cor (Bambu Lab + AMS, ou troca manual
de filamento por camada).

![mockup](preview/mockup.png)

## QR code

O QR foi **decodificado da arte original e reconstruído em geometria nítida** (módulos
quadrados exatos), então continua escaneável depois de impresso.

- Versão: **5 (37 × 37 módulos)**
- Conteúdo: `https://app.tremdeminas.uk/menu/bbeb2bbe-7acb-4cd2-9b18-e6262fc62ee5`
- Validado: a leitura foi confirmada na arte composta e na geometria final.

## Especificações de impressão

| Item | Valor |
|------|-------|
| Tamanho | **120 × 180 mm** |
| Espessura total | **3,0 mm** (base marrom 2,4 mm + camada de cor 0,6 mm) |
| Cores (AMS) | Marrom (fundo), Branco (texto e QR), Laranja (detalhes) |
| Orientação | Deitado, **com a frente para cima** (face colorida = topo) |
| Filamento sugerido | PLA (texturizado) |
| Tempo estimado | 2 h – 3 h |

> **Dica:** para melhor leitura do QR, mantenha bom contraste e evite filamentos
> muito brilhantes na face.

## Arquivos

```
cad/
├── order_pay_qr.3mf        ← projeto completo (3 cores juntas) — abrir no Bambu Studio
├── stl/
│   ├── 01_marrom_base.stl  ← base + fundo + módulos escuros do QR  → MARROM
│   ├── 02_branco.stl       ← texto, painel e módulos claros do QR  → BRANCO
│   └── 03_laranja.stl      ← "COUNTER | BALCÃO", "Faça seu pedido", pílula @  → LARANJA
├── preview/
│   ├── design_flat.png     ← arte plana (vista de topo)
│   └── mockup.png          ← mockup da placa
└── src/
    ├── build_cad.py        ← script que gera a geometria
    └── label_canvas.npy    ← mapa de cores 120×180 usado pelo script
```

Todos os STLs compartilham a **mesma origem**, então encaixam perfeitamente.

## Como imprimir

### Opção A — 3MF (recomendado)
1. Abra `order_pay_qr.3mf` no **Bambu Studio** / OrcaSlicer.
2. As três partes (`brown`, `white`, `orange`) já vêm posicionadas. Atribua um
   filamento a cada uma: marrom, branco e laranja.
3. Mantenha a orientação **frente para cima** (a face com o QR no topo da mesa).
4. Fatie e imprima.

### Opção B — STLs separados
1. Importe os 3 STLs **de uma vez** (eles se alinham sozinhos).
2. Combine como **um único objeto** (parts) e atribua a cor de cada part.
3. Imprima deitado, frente para cima.

## Regenerar a geometria

```bash
pip install pillow numpy opencv-python-headless trimesh shapely mapbox_earcut scipy
cd cad/src && python3 build_cad.py
```

O QR pode ser alterado regenerando `label_canvas.npy` (ver histórico do projeto).
