from k.ui import *
import k.db as kdb
import k.storage as media


class Panel(KPanel):
    def __init__(self, k, anchors, container):
        super().__init__(k, anchors, container)

        self.con_projects = None
        self.refresh()

    def refresh(self, studio_id=None):
        if self.con_projects:
            self.con_projects.kill()

        self.con_projects = pygame_gui.elements.UIScrollingContainer(
            manager=self.k.gui,
            container=self.container,
            anchors=ANCHOR,
            relative_rect=pygame.Rect((10, 10), (500, 400)))

        self.projects = [ ]
        y = 0

        for project in kdb.list_projects():
            entry = Entry(self.k, self.con_projects.get_container(),
                y, project)
            self.projects.append(entry)
            y += entry.get_rect().height

            if studio_id and entry.project_id == studio_id:
                entry.btn_open.disable()

        self.con_projects.set_scrollable_area_dimensions((480, y))

    def click(self, element, target=None):
        for entry in self.projects:
            entry.click(element, target)


class Entry(KPanel):
    def __init__(self, k, container, y, project):
        super().__init__(k, container=container, relative_rect=pygame.Rect(
            (0, y), (480, 60)))

        self.project_id = project['id']

        name = project['name']
        if not name:
            name = ''

        self.btn_open = pygame_gui.elements.UIButton(
            text='Open',
            manager=k.gui,
            container=self.container,
            relative_rect=pygame.Rect((0, 5), (80, 25)))

        self.btn_delete = pygame_gui.elements.UIButton(
            text='Delete',
            manager=k.gui,
            container=self.container,
            relative_rect=pygame.Rect((0, 30), (80, 25)))

        self.lbl_name = pygame_gui.elements.UILabel(
            text=name,
            manager=k.gui,
            container=self.container,
            relative_rect=pygame.Rect((90, 0), (390, 20)))

        self.lbl_created = pygame_gui.elements.UILabel(
            text=f'created: {project["created"]}',
            manager=k.gui,
            container=self.container,
            relative_rect=pygame.Rect((90, 20), (390, 20)))

        self.lbl_updated = pygame_gui.elements.UILabel(
            text=f'updated: {project["updated"]}',
            manager=k.gui,
            container=self.container,
            relative_rect=pygame.Rect((90, 40), (390, 20)))

    def click(self, element, target=None):
        if element == self.btn_open:
            self.btn_open.disable()
            self.k.job(self.open_project)

        elif element == self.btn_delete:
            self.k.confirm(
                self.delete_project,
                'Delete Project?',
                'Delete',
                f'Are you sure you want to delete the project "{self.lbl_name.text}"?'
            )

    def open_project(self):
        panel = self.k.panel_project
        panel.panel_studio.open_project(self.project_id)
        panel.panel_swap(panel.btn_studio, panel.panel_studio)

    def delete_project(self):
        panel = self.k.panel_project
        if panel.panel_studio.project_id == self.project_id:
            panel.panel_studio.close_project()
        media.delete_project_folder(self.project_id)
        kdb.delete_project(self.project_id)
        panel.panel_library.refresh()
        panel.panel_library.hide()
        panel.panel_library.show()
