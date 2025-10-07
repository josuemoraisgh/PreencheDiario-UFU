# UFU Diário – Preenchimento (visual)

Versão enxuta da aplicação que mantém o **navegador Edge aberto** e preenche o diário **visual e interativamente** no portal já autenticado pelo usuário.
Sem discovery de turmas via HTTP nem necessidade de capturar/testar cookie para o fluxo principal.

## Como usar (passo a passo)

1. **Instale dependências** (de preferência em um venv):
   ```bash
   python -m venv .venv
   . .venv/Scripts/activate
   pip install -r requirements.txt
   ```

2. **Edite (se necessário) a URL inicial** em `utils.py` (`GET_URL`). Por padrão está um placeholder.
3. **Execute o app**:
   ```bash
   python main.py
   ```

4. No app:
   - Clique **"Abrir navegador p/ login"** → abre o Edge visível na página inicial. Faça o **login manualmente**.
   - Clique **"Carregar dados (dados.json)"** e escolha um JSON no formato:
     ```json
     {
       "10/06/2025 -P": "Introdução aos conceitos de instrumentação",
       "11/06/2025 -P": "Explicação sobre sensores de temperatura"
     }
     ```
     O painel esquerdo mostrará os itens; você pode **editar**, **adicionar** e **salvar**.
   - **Navegue no Edge** até a turma/diário desejado.
   - Clique **"Preencher diário"** → o app procurará no DOM cada rótulo (ex.: `"10/06/2025 -P"`) e **preencherá o textarea relacionado**.
   - Ao final, tenta clicar em **Salvar/Gravar** e registra o resultado no **painel de Logs** à direita.
   - O **navegador permanece aberto** (padrão).

## Formato do `dados.json`
- As **chaves** devem seguir `DD/MM/AAAA -P`. O app normaliza traços (`– → -`) e espaços duplicados.
- Os **valores** são os textos a lançar no diário.

## Estrutura de pastas
```
ufu_diario_preenchimento_visual/
├─ main.py
├─ requirements.txt
├─ README.md  
└─ services
   ├─ ui.py
   ├─ drivers.py
   ├─ diario.py
   ├─ cookies.py
   └─ utils.py
└─ assets/
   └─ dados_exemplo.json
```

## Gerando um único executável (one-file), janela sem console

### Instale o PyInstaller (no venv)
   ```bash
   python -m pip install --upgrade pip
   python -m pip install pyinstaller
   ```
### Gerar um único executável (one-file), janela sem console
   ```bash
   pyinstaller `
   --noconfirm --clean `
   --onefile --windowed `
   --name "UFU_Diario_Preenchimento" `
   --add-data "assets;assets" `
   --hidden-import selenium `
   --hidden-import selenium.webdriver `
   --hidden-import selenium.webdriver.common.selenium_manager `
   main.py
  ```
## Notas técnicas
- **Selenium (Edge)** em modo visível (Chromium). Usa `webdriver_manager` para gerenciar o driver.
- **Nenhuma descoberta de turmas via HTTP** no fluxo padrão (há funções auxiliares apenas para diagnóstico, desativadas por default).
- Preenchimento visual via **JavaScript**, disparando eventos `input`/`change`.
- UI em **Tkinter**, com **Listbox** à esquerda e **Logs** à direita.
- Compatível com **Python 3.10+**.
