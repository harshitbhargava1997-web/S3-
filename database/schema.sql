-- ============================================================
-- PART A
-- TEACHER PROFESSIONAL DEVELOPMENT
-- ============================================================

create extension if not exists pgcrypto;


-- ============================================================
-- TEACHER PROFILE
-- ============================================================

create table if not exists teacher_pd_profiles (

    id uuid primary key
        default gen_random_uuid(),

    teacher_id text not null unique,

    teacher_name text not null,

    school text,

    state_zone text,

    role text,

    created_at timestamptz
        not null default now(),

    updated_at timestamptz
        not null default now()
);


-- ============================================================
-- MODULE PROGRESS
-- ============================================================

create table if not exists teacher_pd_progress (

    id uuid primary key
        default gen_random_uuid(),

    teacher_id text not null,

    module_id text not null,

    module_status text
        not null default 'not_started',

    current_session integer
        not null default 0,

    progress_percent integer
        not null default 0,

    started_at timestamptz,

    completed_at timestamptz,

    updated_at timestamptz
        not null default now(),

    unique (
        teacher_id,
        module_id
    )
);


-- ============================================================
-- REFLECTIONS
-- ============================================================

create table if not exists teacher_pd_reflections (

    id uuid primary key
        default gen_random_uuid(),

    teacher_id text not null,

    module_id text not null,

    module_name text not null,

    lesson_grade text,

    lesson_subject text,

    lesson_plan_number text,

    lesson_topic text,

    book text,

    page_section text,

    voice_note_path text,

    transcript text,

    learning_objective text,

    bloom_level text,

    objective_quality text,

    teacher_activity text,

    student_activity text,

    practice_apply text,

    review text,

    ai_feedback text,

    ai_score numeric,

    ai_evaluation_json jsonb,

    teacher_confirmed boolean
        not null default false,

    module_status text
        not null default 'draft',

    created_at timestamptz
        not null default now(),

    updated_at timestamptz
        not null default now()
);


-- ============================================================
-- ASSESSMENTS
-- ============================================================

create table if not exists teacher_pd_assessments (

    id uuid primary key
        default gen_random_uuid(),

    teacher_id text not null,

    module_id text not null,

    score integer,

    percentage numeric,

    passed boolean,

    answers_json jsonb,

    completed_at timestamptz
        not null default now()
);


-- ============================================================
-- INDEXES
-- ============================================================

create index if not exists
idx_teacher_pd_progress_teacher
on teacher_pd_progress (
    teacher_id
);


create index if not exists
idx_teacher_pd_reflections_teacher
on teacher_pd_reflections (
    teacher_id
);


create index if not exists
idx_teacher_pd_assessments_teacher
on teacher_pd_assessments (
    teacher_id
);


create index if not exists
idx_teacher_pd_reflections_module
on teacher_pd_reflections (
    module_id
);


-- ============================================================
-- OPTIONAL UPDATED_AT TRIGGER
-- ============================================================

create or replace function update_updated_at_column()
returns trigger
language plpgsql
as $$
begin
    new.updated_at = now();
    return new;
end;
$$;


drop trigger if exists
teacher_pd_profiles_updated_at
on teacher_pd_profiles;

create trigger
teacher_pd_profiles_updated_at
before update on teacher_pd_profiles
for each row
execute function update_updated_at_column();


drop trigger if exists
teacher_pd_progress_updated_at
on teacher_pd_progress;

create trigger
teacher_pd_progress_updated_at
before update on teacher_pd_progress
for each row
execute function update_updated_at_column();


drop trigger if exists
teacher_pd_reflections_updated_at
on teacher_pd_reflections;

create trigger
teacher_pd_reflections_updated_at
before update on teacher_pd_reflections
for each row
execute function update_updated_at_column();
