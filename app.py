from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastui import FastUI, AnyComponent, prebuilt_html, components as c
from fastui.components.display import DisplayMode, DisplayLookup
from fastui.events import GoToEvent, BackEvent, PageEvent
import uvicorn
from helper import db_init
import JobModel
from typing import List

app = FastAPI()
db_init()


# class FilterForm(BaseModel):
#     status: str = Field(json_schema_extra={
#                         'search_url': '/api/forms/search', 'placeholder': 'Filter by status...'})


# class SearchForm(BaseModel):
#     # Send this as "search" query parameter to the backend
#     search: str = Field(json_schema_extra={
#                         'search_url': '/api/forms/search', 'placeholder': 'Search...', 'minLength': 3})


@app.get("/api/", response_model=FastUI, response_model_exclude_none=True)
def users_table(status: str | None = None, search: str | None = None) -> List[AnyComponent]:
    """
    Show a table of all jobs, the frontend will fetch this
    when a user visits `/` to fetch components to render.
    """
    jobs = JobModel.get_all(status=status, search=search)
    filter_form_initial = {}
    if status:
        filter_form_initial['status'] = {'value': status, 'label': status}
    return [
        c.Page(  # Page provides a basic container for components
            components=[
                c.Heading(text='Jobs', level=2),  # renders `<h2>Jobs</h2>`
                # c.ModelForm(
                #     model=FilterForm,
                #     submit_url='.',
                #     initial=filter_form_initial,
                #     method='GOTO',
                #     submit_on_change=True,
                #     display_mode='inline',
                # ),
                # c.ModelForm(
                #     model=SearchForm,
                #     submit_url='.',
                #     method='GOTO',
                #     submit_on_change=True,
                #     display_mode='inline',
                # ),
                c.Table(
                    data=jobs,
                    columns=[
                        DisplayLookup(
                            field='id', on_click=GoToEvent(url='/job/{id}')),
                        DisplayLookup(field='job_text',
                                      mode=DisplayMode.markdown),
                        DisplayLookup(field='status'),
                        DisplayLookup(field='inserted_at',
                                      mode=DisplayMode.date),
                    ],
                ),
            ]
        ),
    ]


@app.get("/api/job/{job_id}", response_model=FastUI, response_model_exclude_none=True)
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

    # Format date
    job.inserted_at = job.inserted_at.strftime('%m/%d/%Y %H:%M:%S')
    if job.applied_at:
        job.applied_at = job.applied_at.strftime('%m/%d/%Y %H:%M:%S')

    # Job_text is markdown, render it as markdown
    job.job_text = c.Markdown(text=job.job_text)

    job.status = c.LinkList(
        links=[
            c.Link(
                components=[c.Text(text='New')],
                on_click=GoToEvent(
                    url=f'/job/{job_id}/update/new'),
                active=job.status == 'new',
            ),
            c.Link(
                components=[c.Text(text='Applied')],
                on_click=GoToEvent(
                    url=f'/job/{job_id}/update/applied'),
                active=job.status == 'applied',
            ),
            c.Link(
                components=[c.Text(text='Discard')],
                on_click=GoToEvent(
                    url=f'/job/{job_id}/update/discarded'),
                active=job.status == 'discarded',
            ),
            c.Link(
                components=[c.Text(text='In interview')],
                on_click=GoToEvent(
                    url=f'/job/{job_id}/update/interviewed'),
                active=job.status == 'interviewed',
            ),
        ],
        mode='tabs',
    )

    return [
        c.Page(
            components=[
                c.Heading(text="Job details", level=2),
                c.Link(components=[c.Text(text='Back')], on_click=BackEvent()),
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
