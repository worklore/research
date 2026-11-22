import { randomBytes } from "node:crypto";
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";

export interface Note {
  id: string;
  title: string;
  body: string;
  tags: string[];
  authorEmail?: string;
  createdAt: string;
  updatedAt: string;
}

export interface NewNote {
  title: string;
  body: string;
  tags?: string[];
  authorEmail?: string;
}

/** Where the notes live. NOTES_FILE overrides the default ./data/notes.json. */
export function notesFile(): string {
  return resolve(process.env.NOTES_FILE ?? "data/notes.json");
}

function load(): Note[] {
  const file = notesFile();
  if (!existsSync(file)) return [];
  return JSON.parse(readFileSync(file, "utf8")) as Note[];
}

function save(notes: Note[]): void {
  const file = notesFile();
  mkdirSync(dirname(file), { recursive: true });
  writeFileSync(file, JSON.stringify(notes, null, 2));
}

export function newId(): string {
  return "n_" + randomBytes(6).toString("hex");
}

export function listNotes(): Note[] {
  return load();
}

export function getNote(id: string): Note | undefined {
  return load().find((n) => n.id === id);
}

export function createNote(input: NewNote): Note {
  const notes = load();
  const now = new Date().toISOString();
  const note: Note = {
    id: newId(),
    title: input.title,
    body: input.body,
    tags: input.tags ?? [],
    ...(input.authorEmail ? { authorEmail: input.authorEmail } : {}),
    createdAt: now,
    updatedAt: now,
  };
  notes.push(note);
  save(notes);
  return note;
}

export function updateNote(id: string, patch: Partial<NewNote>): Note | undefined {
  const notes = load();
  const note = notes.find((n) => n.id === id);
  if (!note) return undefined;
  if (patch.title !== undefined) note.title = patch.title;
  if (patch.body !== undefined) note.body = patch.body;
  if (patch.tags !== undefined) note.tags = patch.tags;
  if (patch.authorEmail !== undefined) note.authorEmail = patch.authorEmail;
  note.updatedAt = new Date().toISOString();
  save(notes);
  return note;
}

export function deleteNote(id: string): boolean {
  const notes = load();
  const next = notes.filter((n) => n.id !== id);
  if (next.length === notes.length) return false;
  save(next);
  return true;
}

export function replaceAll(notes: Note[]): void {
  save(notes);
}
