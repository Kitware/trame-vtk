import nox


# "3.10", "3.11", "3.12"
@nox.session(python=["3.9"])
@nox.parametrize("vtk", ["==9.3.1", "==9.4.1", "==9.4.20250111.dev0"])
def tests(session, vtk):
    session.install(".[dev]")
    session.install("trame")
    session.install("trame-client[test]")
    session.install("trame-vuetify")
    session.install("pytest-asyncio")
    session.install("coverage")
    session.install("pyvista==0.44.1")
    session.install(f"vtk{vtk}", "--extra-index-url", "https://wheels.vtk.org")

    session.run("pytest", "--firefox", "--headless")


@nox.session
def lint(session):
    session.install(".[dev]")
    session.run("pre-commit", "run", "--all-files")
