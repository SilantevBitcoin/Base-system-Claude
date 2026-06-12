# Фронтенд — инструменты по стадиям

Привязка инструментов к стадиям спины (`dev-coding-process-kb.md`) для фронтенд-кода (React/Next/CSS/web). Объявил направление «фронт» → действуешь по этой таблице.

**Роль-агент:** `frontend-engineer` (`~/.claude/agents/`) ведёт стадии 0–6 и дёргает скиллы ниже как руки.

## Привязка

| Стадия | Инструменты |
|---|---|
| 0 Сориентироваться | chrome-devtools-mcp:chrome-devtools (трейс DOM/perf существующего) · react-view-transitions (если анимации) |
| 1 Оформить | composition-patterns (компонентная архитектура: compound / render-props) · vercel:react-best-practices · vercel:nextjs (App Router / RSC) · react-state-management (выбор слоя состояния) |
| 2 Написать (TDD) | composition-patterns · vercel:react-best-practices · react-state-management (RTK / Zustand / Jotai / React Query) · tailwind-patterns (стили v4) · vercel:shadcn (компоненты) · document-skills:frontend-design (визуал) |
| 3 Проверить | document-skills:webapp-testing (Playwright) · a11y-audit (`python scripts/a11y_scanner.py <path>`) · chrome-devtools-mcp:chrome-devtools (Lighthouse / LCP) · бюджеты ↓ |
| 4 Отладить | chrome-devtools-mcp:chrome-devtools + chrome-devtools-mcp:memory-leak-debugging (профайл / память) · fixing-motion-performance (jank / scroll / blur) |
| 5 Ревью | web-design-guidelines (Web Interface Guidelines) · a11y-audit · fixing-motion-performance · рубрика ↓ |
| 6 Завершить | a11y-audit (verify: re-scan, 0 critical/serious) · бюджеты ↓ как gate |

## Рубрика ревью фронта (стадии 3 / 5 / 6)

### Бюджеты (gate)
- **Core Web Vitals:** LCP < 2.5s · INP < 200ms · CLS < 0.1 · FCP < 1.5s · TBT < 200ms.
- **Bundle (gzip JS / CSS):** лендинг < 150kb / 30kb · app-страница < 300kb / 50kb · microsite < 80kb / 15kb.
- **Шрифты:** ≤ 2 семейства · `font-display: swap` · subset · preload только критичного weight.
- **Картинки:** явные width/height · hero `loading=eager` + `fetchpriority=high` · ниже сгиба `loading=lazy` · AVIF/WebP с фолбэком.
- **Анимация:** только compositor-свойства (transform/opacity) · `will-change` узко и снимать после · scroll → IntersectionObserver / scroll-timeline, не scroll-handler.

### Анти-generic дизайн (banned)
Дефолтные card-grid без иерархии · стоковый hero (центр + gradient blob + generic CTA) · немодифицированные дефолты библиотек · плоский layout без глубины · одинаковые radius/spacing/shadow везде · «safe» серое-на-белом + один акцент · dashboard-by-numbers · дефолтные шрифты без причины.

### Требуется (≥ 4 из 10 на значимой поверхности)
Иерархия через контраст масштаба · намеренный ритм spacing · глубина/слои · типографика с характером · цвет семантически · hover/focus/active спроектированы · editorial/bento композиция где уместно · текстура/атмосфера по направлению · движение проясняет flow · дата-виз как часть системы.
