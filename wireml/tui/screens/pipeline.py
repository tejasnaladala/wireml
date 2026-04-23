"""Pipeline screen: show stages, run them, display results."""
from __future__ import annotations

from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import DataTable, Footer, Header, Label, RichLog, Static

from wireml.engine import engine
from wireml.registry import get_schema
from wireml.schema import Pipeline, StageState
from wireml.templates import Template

STATUS_ICON = {
    "idle": "○",
    "running": "●",
    "ok": "✓",
    "error": "✗",
}
STATUS_CLASS = {
    "idle": "muted",
    "running": "warn",
    "ok": "success",
    "error": "error",
}
CATEGORY_CLASS = {
    "data": "data",
    "preprocess": "preprocess",
    "backbone": "backbone",
    "head": "head",
    "eval": "eval",
    "deploy": "deploy",
}


class PipelineScreen(Screen):
    """Linear stage list with a run log and a results panel."""

    BINDINGS = [
        Binding("r", "run", "Run"),
        Binding("escape", "pop_screen", "Back"),
        Binding("q", "app.quit", "Quit"),
    ]

    running: reactive[bool] = reactive(False)

    def __init__(self, template: Template, autorun: bool = False) -> None:
        super().__init__()
        self.template = template
        self.pipeline: Pipeline = template.build()
        self.autorun = autorun

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        yield Vertical(
            Static(
                f"[b]{self.template.title}[/b]   [dim]{self.template.subtitle}[/dim]",
                classes="panel-title",
            ),
            Horizontal(
                Vertical(
                    Label("PIPELINE", classes="panel-title"),
                    Static(id="pipeline-view"),
                    classes="panel",
                ),
                Vertical(
                    Label("RUN LOG", classes="panel-title"),
                    RichLog(id="run-log", highlight=True, markup=True, wrap=True),
                    classes="panel",
                ),
                id="app-grid",
            ),
            Vertical(
                Label("RESULTS", classes="panel-title"),
                DataTable(id="results-table", zebra_stripes=True),
                classes="panel",
                id="results-panel",
            ),
            id="pipeline-root",
        )
        yield Footer()

    def on_mount(self) -> None:
        self._render_pipeline()
        table = self.query_one("#results-table", DataTable)
        table.add_columns("Stage", "Status", "Detail")
        if self.autorun:
            self.run_worker(self._run_pipeline(), exclusive=True, thread=True)

    # ─── rendering ───────────────────────────────────────────────

    def _render_pipeline(self) -> None:
        lines: list[str] = []
        for idx, stage in enumerate(self.pipeline.stages, start=1):
            schema = get_schema(stage.schema_id)
            icon = STATUS_ICON[stage.status]
            status_cls = STATUS_CLASS[stage.status]
            cat_cls = CATEGORY_CLASS.get(schema.category if schema else "", "muted")
            name = schema.name if schema else stage.schema_id
            msg = f" [dim]{stage.message}[/dim]" if stage.message else ""
            lines.append(
                f"[{status_cls}]{icon}[/{status_cls}]  "
                f"[b]{idx}[/b]  "
                f"[{cat_cls}]●[/{cat_cls}] {name}{msg}"
            )
        self.query_one("#pipeline-view", Static).update("\n\n".join(lines))

    def _append_log(self, text: str) -> None:
        self.query_one("#run-log", RichLog).write(text)

    def _update_results(self) -> None:
        table = self.query_one("#results-table", DataTable)
        table.clear()
        for stage in self.pipeline.stages:
            if stage.status != "ok":
                continue
            table.add_row(stage.schema_id, "OK", stage.message or "")

    # ─── actions ─────────────────────────────────────────────────

    def action_run(self) -> None:
        if self.running:
            return
        self.run_worker(self._run_pipeline(), exclusive=True, thread=True)

    def action_pop_screen(self) -> None:
        self.app.pop_screen()

    # ─── execution ───────────────────────────────────────────────

    @work(exclusive=True, thread=True)
    async def _run_pipeline(self) -> None:
        self.running = True
        self.pipeline = self.template.build()  # fresh state per run
        self.app.call_from_thread(self._render_pipeline)
        self.app.call_from_thread(
            self._append_log,
            f"[accent]▶[/accent] running [b]{self.pipeline.name}[/b]",
        )

        def on_progress(stage: StageState) -> None:
            self.app.call_from_thread(self._render_pipeline)
            status_cls = STATUS_CLASS[stage.status]
            icon = STATUS_ICON[stage.status]
            self.app.call_from_thread(
                self._append_log,
                f"[{status_cls}]{icon}[/{status_cls}] {stage.schema_id:<30} "
                f"{stage.message or ''}",
            )

        try:
            engine.execute(self.pipeline, on_progress=on_progress)
        except RuntimeError as exc:
            self.app.call_from_thread(
                self._append_log,
                f"[error]✗[/error] pipeline failed: {exc}",
            )
        else:
            self.app.call_from_thread(
                self._append_log,
                "[success]✓[/success] pipeline complete",
            )
        finally:
            self.app.call_from_thread(self._update_results)
            self.running = False
