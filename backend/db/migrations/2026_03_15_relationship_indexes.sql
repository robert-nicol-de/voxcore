-- Add unique and lookup indexes for relationships table
CREATE UNIQUE INDEX IF NOT EXISTS relationships_unique
ON relationships (
    subject_type,
    subject_id,
    relation,
    object_type,
    object_id
);

CREATE INDEX IF NOT EXISTS relationships_subject_idx
ON relationships (subject_type, subject_id);

CREATE INDEX IF NOT EXISTS relationships_object_idx
ON relationships (object_type, object_id);
