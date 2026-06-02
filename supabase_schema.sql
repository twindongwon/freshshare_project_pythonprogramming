create table if not exists public.profiles (
  userid text primary key,
  nickname text not null,
  neighborhood text,
  created_at timestamptz not null default now()
);

create table if not exists public.listings (
  id text primary key,
  owner_nickname text not null,
  owner_userid text,
  item_name text not null,
  base_food text,
  category text,
  quantity text,
  trade_type text not null default '나눔',
  price_krw integer not null default 0,
  storage_type text not null default '냉장',
  purchase_date date,
  shelf_life_days integer,
  remaining_days integer,
  expiry_date date,
  preservation_method text,
  location text,
  status text not null default 'open',
  created_at timestamptz not null default now()
);

create table if not exists public.messages (
  id text primary key,
  listing_id text not null,
  from_userid text not null,
  from_nick text,
  to_userid text not null,
  to_nick text,
  body text not null,
  ts bigint not null,
  created_at timestamptz not null default now()
);

alter table public.profiles enable row level security;
alter table public.listings enable row level security;
alter table public.messages enable row level security;

create policy "read public listings" on public.listings for select using (true);
create policy "insert public listings" on public.listings for insert with check (true);
create policy "read public messages" on public.messages for select using (true);
create policy "insert public messages" on public.messages for insert with check (true);
create policy "insert profiles" on public.profiles for insert with check (true);
create policy "read profiles" on public.profiles for select using (true);
