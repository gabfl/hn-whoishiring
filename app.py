from typing import List

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastui import FastUI, AnyComponent, prebuilt_html, components as c
from fastui.components.display import DisplayMode, DisplayLookup
from fastui.events import GoToEvent, BackEvent, PageEvent
from fastui.forms import SelectSearchResponse
from pydantic import BaseModel, Field
import uvicorn

from helper import db_init, get_from_cache, set_to_cache, format_dt
from models import JobModel, StatusModel

app = FastAPI()
db_init()


class FilterForm(BaseModel):
    status: str = Field(json_schema_extra={
        'search_url': '/api/search/status', 'placeholder': 'Filter by Status...'})


class SearchForm(BaseModel):
    # Send this as "search" query parameter to the backend
    search: str = Field(json_schema_extra={
                        'placeholder': 'Search...'})


@app.get('/api/search/status', response_model=SelectSearchResponse)
async def status_search_view(request: Request, q: str) -> SelectSearchResponse:
    """ Statuses dropdown search view """

    options = [{'value': s.value, 'label': s.label}
               for s in StatusModel.get_all()]
    return SelectSearchResponse(options=options)


@app.get("/api/", response_model=FastUI, response_model_exclude_none=True)
def users_table(status: str | None = None, search: str | None = None, clear_cache: str | None = None) -> List[AnyComponent]:
    """
    Show a table of all jobs, the frontend will fetch this
    when a user visits `/` to fetch components to render.
    """

    # # Set filters to/from cache
    if status or clear_cache:
        set_to_cache('status', status)
    else:
        status = get_from_cache('status')
    if search or clear_cache:
        set_to_cache('search', search)
    else:
        search = get_from_cache('search')

    # Initial form values
    filter_form_initial = {
        'status': {'value': 'all', 'label': 'All'},
        'search': search
    }

    # Fetch jobs
    jobs = JobModel.get_all(status=status, search=search)

    return [
        c.Page(  # Page provides a basic container for components
            components=[
                # renders `<h2>Jobs</h2>`
                c.Heading(text='Jobs listings (%s)' %
                          (status if status else 'all'), level=2),
                c.ModelForm(
                    model=FilterForm,
                    submit_url='.',
                    initial=filter_form_initial,
                    method='GOTO',
                    submit_on_change=True,
                    display_mode='inline',
                ),
                c.ModelForm(
                    model=SearchForm,
                    submit_url='.',
                    initial=filter_form_initial,
                    method='GOTO',
                    submit_on_change=True,
                    display_mode='inline',
                ),
                c.Div(
                    components=[
                        c.Text(
                            text='%d jobs match the criteria ' % len(jobs)),
                        c.Link(
                            components=[c.Text(text='(Clear filters)')],
                            on_click=GoToEvent(url='?clear_cache=1'),
                        ),
                    ]
                ),
                c.Table(
                    data=jobs,
                    columns=[
                        DisplayLookup(
                            field='id', on_click=GoToEvent(url='/job/{id}')),
                        DisplayLookup(field='job_text',
                                      mode=DisplayMode.markdown),
                        DisplayLookup(field='status'),
                        DisplayLookup(field='inserted_at'),
                    ],
                ),
            ]
        ),
    ]


@ app.get("/api/job/{job_id}", response_model=FastUI, response_model_exclude_none=True)
# @app.get("/job/{job_id}", response_model=FastUI, response_model_exclude_none=True)
def job_profile(job_id: int) -> list[AnyComponent]:
    """
    Job detail page, the frontend will fetch this
    when a user visits `/job/{job_id}` to fetch components to render.
    """

    try:
        job = JobModel.get(job_id)
    except StopIteration:
        raise HTTPException(status_code=404, detail="Job not found")

    # Job_text is markdown, render it as markdown
    job.job_text = c.Markdown(text=job.job_text)

    # Links
    links = []
    for status in StatusModel.get_all():
        links.append(
            c.Link(
                components=[c.Text(text=status.label)],
                on_click=GoToEvent(url=f'/job/{job_id}/update/{status.value}'),
                active=job.status == status.value,
            )
        )

    job.status = c.LinkList(
        links=links,
        mode='tabs',
    )

    job.inserted_at = format_dt(job.inserted_at)
    job.updated_at = format_dt(job.updated_at)
    job.applied_at = format_dt(job.applied_at)

    return [
        c.Page(
            components=[
                c.Heading(text="Job details", level=2),
                c.Link(
                    components=[c.Text(text='Back to listings')],
                    on_click=GoToEvent(url='/')
                ),
                c.Details(data=job),
            ]
        ),
    ]


@ app.get("/api/job/{job_id}/update/{status}", response_model=FastUI)
async def update_status(job_id: int, status: str) -> list[AnyComponent]:
    JobModel.update(job_id, status)

    # Redirect
    # return RedirectResponse(url=f'/job/{job_id}')
    return [c.FireEvent(event=GoToEvent(url=f'/job/{job_id}'))]


@ app.get('/{path:path}')
async def html_landing() -> HTMLResponse:
    """Simple HTML page which serves the React app, comes last as it matches all paths."""
    return HTMLResponse(prebuilt_html(title='Who Is Hiring?'))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
