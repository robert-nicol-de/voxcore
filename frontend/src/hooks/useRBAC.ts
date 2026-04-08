// RBAC hook for permission checks
import { useMemo } from "react";
import { getUser } from "../utils/auth";

export function useRBAC() {
  const user = useMemo(() => getUser(), []);

  function can(action: string) {
    return user?.permissions?.includes(action);
  }

  return { can };
}
