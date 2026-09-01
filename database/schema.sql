CREATE TABLE assessments (
    id SERIAL PRIMARY KEY,
    code VARCHAR(40) NOT NULL UNIQUE,
    title VARCHAR(160) NOT NULL,
    equipment VARCHAR(120) NOT NULL,
    form_url VARCHAR(500),
    passing_score DOUBLE PRECISION NOT NULL DEFAULT 70
);

CREATE TABLE submissions (
    id SERIAL PRIMARY KEY,
    assessment_id INTEGER NOT NULL REFERENCES assessments(id),
    participant_code VARCHAR(40) NOT NULL,
    client VARCHAR(100) NOT NULL,
    instructor VARCHAR(100) NOT NULL,
    score DOUBLE PRECISION NOT NULL CHECK (score BETWEEN 0 AND 100),
    submitted_at TIMESTAMP NOT NULL
);

CREATE INDEX ix_submissions_assessment_id ON submissions(assessment_id);
CREATE INDEX ix_submissions_submitted_at ON submissions(submitted_at);

