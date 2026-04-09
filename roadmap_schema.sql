-- Roadmap tables for the AI Resume Analyzer

-- Table to store roadmap templates for different job roles
CREATE TABLE IF NOT EXISTS roadmap_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_role TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    difficulty_level TEXT CHECK(difficulty_level IN ('beginner', 'intermediate', 'advanced')),
    estimated_duration INTEGER, -- in weeks
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table to store individual roadmap steps/milestones
CREATE TABLE IF NOT EXISTS roadmap_steps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    template_id INTEGER NOT NULL,
    step_order INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    category TEXT, -- e.g., 'technical', 'soft_skills', 'certification'
    estimated_time INTEGER, -- in hours
    resources TEXT, -- JSON formatted list of resources
    prerequisites TEXT, -- JSON formatted list of prerequisite step IDs
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (template_id) REFERENCES roadmap_templates (id) ON DELETE CASCADE
);

-- Table to track user progress on roadmaps
CREATE TABLE IF NOT EXISTS user_roadmaps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    template_id INTEGER NOT NULL,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    status TEXT CHECK(status IN ('not_started', 'in_progress', 'completed')) DEFAULT 'not_started',
    progress_percentage REAL DEFAULT 0.0,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (template_id) REFERENCES roadmap_templates (id) ON DELETE CASCADE
);

-- Table to track progress on individual roadmap steps
CREATE TABLE IF NOT EXISTS user_roadmap_steps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_roadmap_id INTEGER NOT NULL,
    step_id INTEGER NOT NULL,
    status TEXT CHECK(status IN ('not_started', 'in_progress', 'completed')) DEFAULT 'not_started',
    started_at TIMESTAMP NULL,
    completed_at TIMESTAMP NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_roadmap_id) REFERENCES user_roadmaps (id) ON DELETE CASCADE,
    FOREIGN KEY (step_id) REFERENCES roadmap_steps (id) ON DELETE CASCADE
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_roadmap_templates_job_role ON roadmap_templates (job_role);
CREATE INDEX IF NOT EXISTS idx_roadmap_steps_template ON roadmap_steps (template_id, step_order);
CREATE INDEX IF NOT EXISTS idx_user_roadmaps_user ON user_roadmaps (user_id, template_id);
CREATE INDEX IF NOT EXISTS idx_user_roadmap_steps_user ON user_roadmap_steps (user_roadmap_id, step_id);