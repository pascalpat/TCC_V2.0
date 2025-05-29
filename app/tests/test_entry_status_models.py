import datetime
import pytest
from app import db
from app.models.core_models import Project, ActivityCode
from app.models.work_orders_models import WorkOrder
from app.models.MaterialEntry import MaterialEntry
from app.models.EquipmentEntry_models import EquipmentEntry
from app.models.WorkOrderEntry import WorkOrderEntry
from app.models.WorkerEntry_models import WorkerEntry
from app.models.SubcontractorEntry import SubcontractorEntry
from app.models.daily_models import DailyNoteEntry
from app.models.subcontractor_models import Subcontractor

def create_project():
    p = Project(name='Test Project', project_number='TP1', category='Test')
    db.session.add(p)
    db.session.commit()
    return p


def create_activity(project):
    ac = ActivityCode(code='AC1', description='test', project_id=project.id)
    db.session.add(ac)
    db.session.commit()
    return ac


def create_work_order(project, ac):
    wo = WorkOrder(project_id=project.id, sequential_number='WO1', description='desc', type='change_order', activity_code_id=ac.id)
    db.session.add(wo)
    db.session.commit()
    return wo


def create_subcontractor(project):
    sc = Subcontractor(name='Sub', project_id=project.id)
    db.session.add(sc)
    db.session.commit()
    return sc


@pytest.fixture
def setup_entities(app):
    with app.app_context():
        project = create_project()
        activity = create_activity(project)
        work_order = create_work_order(project, activity)
        subcontractor = create_subcontractor(project)
        return project, activity, work_order, subcontractor


def test_crud_entry_progress_models(app, setup_entities):
    project, activity, work_order, subcontractor = setup_entities
    with app.app_context():
        date = datetime.date.today()

        # MaterialEntry
        m = MaterialEntry(project_id=project.id, date_of_report=date)
        db.session.add(m)
        db.session.commit()
        m.status = 'in_progress'
        db.session.commit()
        assert MaterialEntry.query.get(m.id).status == 'in_progress'
        db.session.delete(m)
        db.session.commit()
        assert MaterialEntry.query.get(m.id) is None

        # EquipmentEntry
        e = EquipmentEntry(project_id=project.id, date_of_report=date)
        db.session.add(e)
        db.session.commit()
        e.status = 'completed'
        db.session.commit()
        assert EquipmentEntry.query.get(e.id).status == 'completed'
        db.session.delete(e)
        db.session.commit()
        assert EquipmentEntry.query.get(e.id) is None

        # WorkerEntry
        w = WorkerEntry(project_id=project.id, date_of_report=date)
        db.session.add(w)
        db.session.commit()
        w.status = 'completed'
        db.session.commit()
        assert WorkerEntry.query.get(w.id).status == 'completed'
        db.session.delete(w)
        db.session.commit()
        assert WorkerEntry.query.get(w.id) is None

        # SubcontractorEntry
        s = SubcontractorEntry(project_id=project.id, subcontractor_id=subcontractor.id)
        db.session.add(s)
        db.session.commit()
        s.status = 'in_progress'
        db.session.commit()
        assert SubcontractorEntry.query.get(s.id).status == 'in_progress'
        db.session.delete(s)
        db.session.commit()
        assert SubcontractorEntry.query.get(s.id) is None

        # WorkOrderEntry
        woe = WorkOrderEntry(work_order_id=work_order.id, activity_code_id=activity.id)
        db.session.add(woe)
        db.session.commit()
        woe.status = 'completed'
        db.session.commit()
        assert WorkOrderEntry.query.get(woe.id).status == 'completed'
        db.session.delete(woe)
        db.session.commit()
        assert WorkOrderEntry.query.get(woe.id) is None


def test_crud_daily_note_status(app, setup_entities):
    project, activity, _, _ = setup_entities
    with app.app_context():
        date = datetime.date.today()
        note = DailyNoteEntry(project_id=project.id, date_of_report=date, content='test')
        db.session.add(note)
        db.session.commit()
        note.status = 'committed'
        db.session.commit()
        assert DailyNoteEntry.query.get(note.id).status == 'committed'
        db.session.delete(note)
        db.session.commit()
        assert DailyNoteEntry.query.get(note.id) is None
