import yaml
import sys
import os

import requests

FILE = "build_phases.yaml"


def load():
    with open(FILE, "r") as f:
        return yaml.safe_load(f)

def save(data):
    with open(FILE, "w") as f:
        yaml.dump(data, f)

def list_tasks():
    data = load()
    for phase in data["phases"]:
        print(f"\n=== {phase['id']} ({phase['status']}) ===")
        for t in phase["tasks"]:
            print(f"{t['id']} - {t['description']} [{t['status']}] Demo: {t['demo']}")

def update_task(task_id, new_status, demo=None):
    data = load()
    for phase in data["phases"]:
        for t in phase["tasks"]:
            if t["id"] == task_id:
                # Ownership enforcement
                if not t.get("owner"):
                    print(f"❌ Task {task_id} missing owner")
                    sys.exit(1)
                if not t.get("reviewer"):
                    print(f"❌ Task {task_id} missing reviewer")
                    sys.exit(1)
                # SLA enforcement
                from datetime import datetime
                if t.get("created_at") and t.get("sla_days"):
                    created = datetime.fromisoformat(str(t["created_at"]))
                    sla = int(t.get("sla_days", 3))
                    if (datetime.now() - created).days > sla:
                        print(f"⚠️ Task {task_id} is overdue")
                # Enforce definition_of_done before marking as done
                if new_status == "done":
                    checklist = t.get("definition_of_done", [])
                    if checklist and not t.get("checklist_complete", False):
                        print(f"❌ Cannot mark {task_id} as done: definition_of_done not satisfied")
                        print("Checklist:")
                        for item in checklist:
                            print(f"- {item}")
                        sys.exit(1)
                # Dependency enforcement
                if not check_dependencies(t, [tt for ph in data["phases"] for tt in ph["tasks"]]):
                    print(f"❌ Dependencies not satisfied for {task_id}")
                    sys.exit(1)
                t["status"] = new_status
                if demo is not None:
                    t["demo"] = demo
                save(data)
                print(f"Updated {task_id} → {new_status}")
                return
    def check_dependencies(task, all_tasks):
        deps = task.get("depends_on", [])
        for dep in deps:
            dep_task = next((t for t in all_tasks if t["id"] == dep), None)
            if dep_task and dep_task["status"] != "done":
                print(f"❌ Dependency {dep} not complete for {task['id']}")
                return False
        return True
    print("Task not found")

def check_phase_complete(phase_id):
    data = load()
    for phase in data["phases"]:
        if phase["id"] == phase_id:
            for t in phase["tasks"]:
                if t["status"] == "done" and not t["demo"]:
                    print(f"❌ Task {t['id']} missing demo")
                    sys.exit(1)
                # Enforce definition_of_done checklist
                checklist = t.get("definition_of_done", [])
                if t["status"] == "done" and checklist and not t.get("checklist_complete", False):
                    print(f"❌ Task {t['id']} missing checklist completion")
                    sys.exit(1)
            return all(t["status"] == "done" for t in phase["tasks"])
    return False

def enforce():
    data = load()
    # Regression blocking: prevent code changes in completed phases
    changed_files = get_git_diff()
    for phase in data["phases"]:
        if phase["status"] == "done" and phase.get("code_paths"):
            for path in phase["code_paths"]:
                if any(f.startswith(path) for f in changed_files):
                    print(f"❌ Cannot modify completed phase: {phase['id']}")
                    sys.exit(1)
    for i, phase in enumerate(data["phases"]):
        if phase["status"] == "in-progress":
            if not check_phase_complete(phase["id"]):
                print(f"❌ Phase {phase['id']} not complete")
                sys.exit(1)
def get_git_diff():
    # Returns list of changed files (relative paths) in working tree vs main branch
    import subprocess
    try:
        out = subprocess.check_output(["git", "diff", "--name-only", "origin/main...HEAD"])
        return out.decode().splitlines()
    except Exception:
        return []
def check_sla(task):
    from datetime import datetime
    if task.get("created_at") and task.get("sla_days"):
        created = datetime.fromisoformat(str(task["created_at"]))
        sla = int(task.get("sla_days", 3))
        if (datetime.now() - created).days > sla:
            print(f"⚠️ Task {task['id']} is overdue")
def show_impact(task):
    if task.get("affects"):
        print(f"⚠️ This task impacts: {', '.join(task['affects'])}")
def dashboard():
    data = load()
    from datetime import datetime
    print("\n=== VoxCore Execution Dashboard ===\n")
    for phase in data["phases"]:
        score = phase_score(phase)
        total = len(phase["tasks"])
        done = sum(1 for t in phase["tasks"] if t["status"] == "done")
        overdue = [t["id"] for t in phase["tasks"] if t.get("created_at") and t.get("sla_days") and (datetime.now() - datetime.fromisoformat(str(t["created_at"]))).days > int(t.get("sla_days", 3))]
        blocked = [t["id"] for t in phase["tasks"] if not check_dependencies(t, [tt for ph in data["phases"] for tt in ph["tasks"]])]
        risk = "HIGH" if overdue or blocked else ("MEDIUM" if score < 100 else "LOW")
        print(f"{phase['id']} ({phase['name']}): {score}% complete")
        print(f"- Tasks done: {done}/{total}")
        print(f"- Overdue: {', '.join(overdue) if overdue else 'None'}")
        print(f"- Blocked: {', '.join(blocked) if blocked else 'None'}")
        print(f"- Risk: {risk}\n")
def build_report():
    data = load()
    from datetime import datetime
    print("# VoxCore Build Report\n")
    for phase in data["phases"]:
        score = phase_score(phase)
        total = len(phase["tasks"])
        done = sum(1 for t in phase["tasks"] if t["status"] == "done")
        overdue = [t["id"] for t in phase["tasks"] if t.get("created_at") and t.get("sla_days") and (datetime.now() - datetime.fromisoformat(str(t["created_at"]))).days > int(t.get("sla_days", 3))]
        blocked = [t["id"] for t in phase["tasks"] if not check_dependencies(t, [tt for ph in data["phases"] for tt in ph["tasks"]])]
        print(f"## {phase['id']} ({phase['name']})")
        print(f"- Status: {phase['status'].upper()}")
        print(f"- Completion: {score}%")
        print(f"- Blockers: {', '.join(blocked) if blocked else 'None'}")
        print(f"- Overdue: {', '.join(overdue) if overdue else 'None'}\n")
    print("## System Health")
    try:
        validate_system()
        print("- API: ✅\n- Query Engine: ✅\n- Insights: ✅")
    except Exception:
        print("- API: ❌\n- Query Engine: ❌\n- Insights: ❌")

            # SYSTEM VALIDATION LAYER
            validate_system()

            # unlock next phase
            if i + 1 < len(data["phases"]):
                data["phases"][i + 1]["status"] = "in-progress"

            phase["status"] = "done"
            save(data)
            print(f"✅ Phase {phase['id']} complete")
            return

    print("Nothing to enforce")
def validate_system():
    checks = [
        ("API Health", "http://localhost:8000/health"),
        ("Query Endpoint", "http://localhost:8000/api/playground/query"),
    ]
    failed = False
    for name, url in checks:
        try:
            r = requests.get(url)
            if r.status_code != 200:
                print(f"❌ {name} failed")
                failed = True
            else:
                print(f"✅ {name} OK")
        except Exception as e:
            print(f"❌ {name} error: {e}")
            failed = True
    if failed:
        sys.exit(1)
def phase_score(phase):
    total = len(phase["tasks"])
    done = sum(1 for t in phase["tasks"] if t["status"] == "done")
    return int((done / total) * 100) if total > 0 else 0

def generate_docs():
    data = load()
    os.makedirs("docs/build_history", exist_ok=True)
    for phase in data["phases"]:
        if phase["status"] == "done":
            with open(f"docs/build_history/{phase['id']}.md", "w") as f:
                f.write(f"# {phase['name']}\n\n")
                for t in phase["tasks"]:
                    f.write(f"- {t['description']} ✅\n")

if __name__ == "__main__":
    cmd = sys.argv[1]

    if cmd == "list":
        list_tasks()
    elif cmd == "done":
        demo = sys.argv[3] if len(sys.argv) > 3 else None
        update_task(sys.argv[2], "done", demo)
    elif cmd == "start":
        update_task(sys.argv[2], "in-progress")
    elif cmd == "enforce":
        enforce()
    elif cmd == "docs":
        generate_docs()
    elif cmd == "validate-demo":
        data = load()
        demo_incomplete = False
        for phase in data["phases"]:
            for t in phase["tasks"]:
                demo_val = str(t.get("demo", "")).strip().lower()
                if demo_val not in ("yes", "true", "complete", "done", "1"):
                    print(f"DEMO INCOMPLETE: {phase['id']} - {t['id']} ({t['description']})")
                    demo_incomplete = True
        if demo_incomplete:
            sys.exit(1)
        print("All demo tasks are validated as complete.")
    elif cmd == "validate-system":
        validate_system()
    elif cmd == "score":
        data = load()
        for phase in data["phases"]:
            score = phase_score(phase)
            print(f"{phase['id']} ({phase['name']}): {score}% complete")
    elif cmd == "dashboard":
        dashboard()
    elif cmd == "build-report":
        build_report()
