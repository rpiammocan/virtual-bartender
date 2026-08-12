const API_BASE = import.meta.env.VITE_API_BASE ?? "/api";

export type Ingredient = {
  id: number;
  name: string;
  category?: string | null;
  is_user_created: boolean;
  is_active: boolean;
};

export type InventoryItem = {
  id: number;
  ingredient_id: number;
  context_type: string;
  context_id?: number | null;
  quantity?: number | null;
  unit_id?: number | null;
  have: boolean;
  notes?: string | null;
};

export type BarSession = {
  id: number;
  name: string;
  session_date: string;
  source_type: string;
  created_at: string;
  updated_at: string;
};

export type RecipeMatch = {
  recipe_id: number;
  recipe_name: string;
  status: string;
  missing_required: string[];
  available_required: string[];
  optional_missing: string[];
  substitutions: string[];
  quantity_issues: string[];
  variant_recipe_id?: number | null;
  variant_recipe_name?: string | null;
  explanation: string;
};

export type RecipeDetail = {
  id: number;
  name: string;
  description?: string | null;
  recipe_type: string;
  source_type: string;
  instructions?: string | null;
  image_path?: string | null;
  favorite: boolean;
  ingredients: {
    id: number;
    ingredient_id: number;
    ingredient_name: string;
    quantity?: number | null;
    unit?: string | null;
    is_optional: boolean;
    notes?: string | null;
  }[];
};

export type ShoppingItem = {
  id: number;
  ingredient_id?: number | null;
  custom_name?: string | null;
  quantity?: number | null;
  unit_id?: number | null;
  category?: string | null;
  purchased: boolean;
  created_at: string;
};

export type HistoryItem = {
  id: number;
  recipe_id: number;
  session_id?: number | null;
  rating?: number | null;
  notes?: string | null;
  made_at: string;
};

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options?.headers ?? {}),
    },
    ...options,
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `Request failed: ${response.status}`);
  }

  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export const api = {
  ingredients: {
    list: () => request<Ingredient[]>("/ingredients"),
    create: (name: string, category?: string) =>
      request<Ingredient>("/ingredients", {
        method: "POST",
        body: JSON.stringify({ name, category: category || null }),
      }),
  },

  inventory: {
    listMyBar: () => request<InventoryItem[]>("/inventory?context_type=my_bar"),
    listSession: (sessionId: number) =>
      request<InventoryItem[]>(`/inventory?context_type=tonight_bar&context_id=${sessionId}`),
    add: (payload: { ingredient_id: number; context_type: string; context_id?: number | null; quantity?: number | null }) =>
      request<InventoryItem>("/inventory", {
        method: "POST",
        body: JSON.stringify({
          ...payload,
          unit_id: null,
          have: true,
          notes: null,
        }),
      }),
    updateQuantity: (id: number, quantity: number | null) =>
      request<InventoryItem>(`/inventory/${id}`, {
        method: "PATCH",
        body: JSON.stringify({ quantity }),
      }),
    remove: (id: number) => request<void>(`/inventory/${id}`, { method: "DELETE" }),
  },

  bars: {
    list: () => request<BarSession[]>("/bars/tonight"),
    create: (name: string, sessionDate: string) =>
      request<BarSession>("/bars/tonight", {
        method: "POST",
        body: JSON.stringify({ name, session_date: sessionDate, source_type: "tonight" }),
      }),
    copyMyBar: (id: number) => request<void>(`/bars/tonight/${id}/copy-my-bar`, { method: "POST" }),
    remove: (id: number) => request<void>(`/bars/tonight/${id}`, { method: "DELETE" }),
  },

  recipes: {
    list: () => request<any[]>("/recipes"),
    get: (id: number) => request<RecipeDetail>(`/recipes/${id}`),
  },

  matches: {
    myBar: () => request<RecipeMatch[]>("/matches?context_type=my_bar"),
    session: (sessionId: number) =>
      request<RecipeMatch[]>(`/matches?context_type=tonight_bar&context_id=${sessionId}`),
  },

  favorites: {
    list: () => request<{ recipe_id: number; name: string }[]>("/favorites"),
    add: (id: number) => request(`/favorites/${id}`, { method: "POST" }),
    remove: (id: number) => request<void>(`/favorites/${id}`, { method: "DELETE" }),
  },

  history: {
    list: () => request<HistoryItem[]>("/history"),
    add: (payload: { recipe_id: number; session_id?: number | null; rating?: number | null; notes?: string | null }) =>
      request<HistoryItem>("/history", {
        method: "POST",
        body: JSON.stringify(payload),
      }),
  },

  shopping: {
    list: () => request<ShoppingItem[]>("/shopping"),
    addManual: (name: string, category?: string) =>
      request<ShoppingItem>("/shopping", {
        method: "POST",
        body: JSON.stringify({
          ingredient_id: null,
          custom_name: name,
          quantity: null,
          unit_id: null,
          category: category || "Other",
        }),
      }),
    markPurchased: (id: number, purchased: boolean) =>
      request<ShoppingItem>(`/shopping/${id}/purchased?purchased=${purchased}`, {
        method: "PATCH",
      }),
    remove: (id: number) => request<void>(`/shopping/${id}`, { method: "DELETE" }),
  },




  display: {
    recipe: (id: number, metric: boolean) =>
      request<any>(`/display/recipe/${id}?metric=${metric}`),
  },

  exports: {
    markdownUrl: (id: number) => `${API_BASE}/export/recipe/${id}.md`,
    textUrl: (id: number) => `${API_BASE}/export/recipe/${id}.txt`,
  },

  backups: {
    list: () => request<any[]>("/backups"),
    create: () => request<any>("/backups", { method: "POST" }),
    restore: (id: number) => request<any>(`/backups/${id}/restore`, { method: "POST" }),
  },

  shoppingSuggestions: {
    myBar: () => request<any[]>("/shopping-suggestions?context_type=my_bar"),
    session: (id: number) =>
      request<any[]>(`/shopping-suggestions?context_type=tonight_bar&context_id=${id}`),
  },

  importer: {
    fromUrl: (url: string) =>
      request<any>("/import/url", {
        method: "POST",
        body: JSON.stringify({ url }),
      }),
    save: (payload: any) =>
      request<any>("/import/save", {
        method: "POST",
        body: JSON.stringify(payload),
      }),
  },

  surprise: {
    myBar: () => request<any>("/surprise?context_type=my_bar"),
    session: (id: number) => request<any>(`/surprise?context_type=tonight_bar&context_id=${id}`),
  },
};
