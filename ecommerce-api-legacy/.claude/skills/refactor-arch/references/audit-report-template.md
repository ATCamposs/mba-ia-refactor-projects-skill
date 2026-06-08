# Template — Relatório de Auditoria (Fase 2)

Use este template **literal** ao emitir o relatório no console e ao persistir o arquivo. Substitua placeholders `<...>` por valores reais. **Não modifique arquivos do projeto nesta fase.**

## Ordenação obrigatória

Listar findings na seção `## Findings` ordenados por severidade:

1. **CRITICAL** (todos primeiro)
2. **HIGH**
3. **MEDIUM**
4. **LOW**

Dentro da mesma severidade, ordenar por caminho de arquivo alfabético.

## Formato do relatório

```markdown
================================
ARCHITECTURE AUDIT REPORT
================================
Project: <nome do diretório do projeto ou identificador>
Stack:   <linguagem> + <framework e versão se disponível>
Files:   <N> analyzed | ~<LOC> lines of code

## Summary
CRITICAL: <n> | HIGH: <n> | MEDIUM: <n> | LOW: <n>

## Findings

### [CRITICAL] <título curto do achado>
File: <caminho/relativo/arquivo.ext>:<linha>[-<linha_fim>]
Description: <o que foi encontrado — 1–3 frases>
Impact: <risco arquitetural, segurança ou manutenção>
Recommendation: <ação concreta alinhada ao catálogo de anti-patterns>

### [HIGH] <título>
File: <arquivo>:<linha>
Description: ...
Impact: ...
Recommendation: ...

### [MEDIUM] <título>
File: <arquivo>:<linha>
Description: ...
Impact: ...
Recommendation: ...

### [LOW] <título>
File: <arquivo>:<linha>
Description: ...
Impact: ...
Recommendation: ...

================================
Total: <N> findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

## Regras por campo

| Campo | Regra |
|---|---|
| `File` | **Obrigatório** `arquivo:linha` ou `arquivo:linha-linha_fim`; caminho relativo ao projeto auditado |
| `Description` | Evidência objetiva (trecho, padrão grep, comportamento) |
| `Impact` | Alinhar à escala do README raiz (CRITICAL = segurança/arquitetura grave, etc.) |
| `Recommendation` | Ação da Fase 3 ou "documentar como contrato intencional" quando aplicável |
| `Summary` | Contagens devem bater com o total de findings |

## Persistência do relatório

Salvar cópia Markdown **sempre na raiz do monorepo**, não dentro do subprojeto:

| Projeto auditado | Arquivo de saída |
|---|---|
| E-commerce Flask flat (projeto 1) | `reports/audit-project-1.md` |
| LMS Express (projeto 2) | `reports/audit-project-2.md` |
| Task Manager Flask parcial (projeto 3) | `reports/audit-project-3.md` |

**Quando `cwd` é o subprojeto** (ex.: `ecommerce-api-legacy/`), usar path relativo `../reports/audit-project-2.md` ou resolver a raiz do monorepo subindo até encontrar `reports/` ou os três projetos irmãos.

Criar diretório `reports/` na raiz se não existir.

## Gate HITL (obrigatório)

Após imprimir o relatório e persistir o arquivo:

1. **PARAR** — não criar, editar nem deletar arquivos do projeto.
2. Exibir exatamente: `Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]`
3. Aguardar resposta explícita do humano (`y`, `yes`, `sim` → prosseguir; qualquer outra → encerrar sem Fase 3).
4. Se o fluxo foi invocado como automação sem humano no loop, registrar que a Fase 3 está **bloqueada** até confirmação.

**Proibido na Fase 2:** refatorar, mover arquivos, extrair módulos ou "corrigir" smells — apenas relatar.
