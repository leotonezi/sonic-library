import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { getBackendUrl } from "@/lib/api-client";
import type { User } from "@/types";
import AdminDashboard from "./admin-dashboard";

interface ApiResponse<T> {
  data: T;
}

export default async function AdminPage() {
  const cookieStore = await cookies();
  const accessToken = cookieStore.get("access_token")?.value ?? "";

  let isAdmin = false;

  try {
    const res = await fetch(`${getBackendUrl()}/users/me`, {
      headers: {
        Cookie: `access_token=${accessToken}`,
      },
      cache: "no-store",
    });

    if (!res.ok) {
      redirect("/login");
    }

    const { data: user }: ApiResponse<User> = await res.json();
    isAdmin = user.is_admin === true;
  } catch {
    redirect("/login");
  }

  if (!isAdmin) {
    redirect("/books");
  }

  return <AdminDashboard />;
}
