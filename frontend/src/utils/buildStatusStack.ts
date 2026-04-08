// Utility to flatten all tasks from build phases into a flat array for StatusStack
export function buildStatusStack(phases: any[]) {
  const tasks: any[] = [];
  phases.forEach((phase) => {
    if (phase.tasks) {
      phase.tasks.forEach((task: any) => {
        tasks.push({
          id: task.id,
          description: task.description,
          status: task.status,
          owner: task.owner,
        });
      });
    }
  });
  return tasks;
}
