<div style="text-align: center;">

МІНІСТЕРСТВО ОСВІТИ І НАУКИ УКРАЇНИ

НАЦІОНАЛЬНИЙ УНІВЕРСИТЕТ "ЛЬВІВСЬКА ПОЛІТЕХНІКА"

</div>

<br/>
<br/>
<br/>
<br/>

# <div style="text-align: center;">ЛЕКЦІЯ 13. Системи AI агентів, частина 2: додаткові матеріали</div>

<br/>
<br/>

### <p style="text-align: center;">Львів -- 2025</p>

<div style="page-break-after: always;"></div>

# Лекція курсу "Штучний інтелект в ігрових застосунках" 2025-13

Задача:

Передача графічних даних з простого інтуітивного редактора типа TLDRAW в ШІ агент, який згенерує команди для відтворення намальованої сцени в Blender.

## 1. Формування вхідних даних для прикладу "3D-редактор"

Розширення ідеї контролювати 3Д-моделювання методами іншими, ніж безпосередньо GUI редактора, призводить, наприклад, до ось таких комплексних систем:

https://tryvibedraw.com/create

Як побудований VibeDraw?

https://github.com/martin226/vibe-draw

Реалізація генератора 3D-ассетів від Microsoft:

https://github.com/microsoft/TRELLIS/tree/main

## 2. Генералізація до мультиагентних систем

Система мультиагентної взаємодії від Microsoft:

https://github.com/CopilotKit/open-multi-agent-canvas

## 3. Простіше, будь ласка

Можна пробувати вирішити ту саму задачу через вкрай примітивні універсальні взаємодії через протокол MCP, наприклад створення скріншотів:

https://chromewebstore.google.com/detail/browser-mcp-automate-your/bjfgambnhccakkhmkepdoekmckoijdlc

https://github.com/sethbang/mcp-screenshot-server

## 4. Складніше, будь ласка

А можна взти ідею скріншотів і побудувати на ній цілу систему збору індивідуального контексту через запис відео, мікрофону і взагалі всієї інформації яку тільки
можна зібрати про користувача системи:

https://www.reddit.com/r/ClaudeAI/comments/1hpxueh/mcp_to_use_claude_with_your_247_desktop_context/
