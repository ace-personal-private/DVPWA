export interface User {
  id: number;
  email: string;
  username: string;
  role: string;
  balance: number;
  avatar_path: string | null;
  created_at: string;
  password_hash?: string;
}

export interface Stock {
  id: number;
  ticker: string;
  name: string;
  price: number;
  logo_url: string | null;
}

export interface Holding {
  id: number;
  user_id: number;
  stock_id: number;
  quantity: number;
  avg_price: number;
}

export interface Order {
  id: number;
  user_id: number;
  stock_id: number;
  side: string;
  quantity: number;
  price: number;
  status: string;
  created_at: string;
}

export interface Transaction {
  id: number;
  user_id: number;
  type: string;
  amount: number;
  balance_after: number;
  created_at: string;
}

export interface SupportTicket {
  id: number;
  user_id: number;
  subject: string;
  message: string;
  status: string;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}
