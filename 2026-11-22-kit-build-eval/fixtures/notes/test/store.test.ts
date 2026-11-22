import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { createNote, deleteNote, getNote, listNotes, updateNote } from "../src/store.js";

let dir: string;
beforeEach(() => {
  dir = mkdtempSync(join(tmpdir(), "notes-test-"));
  process.env.NOTES_FILE = join(dir, "notes.json");
});
afterEach(() => rmSync(dir, { recursive: true, force: true }));

describe("store", () => {
  it("creates, reads, updates and deletes a note", () => {
    const n = createNote({ title: "Hello", body: "World" });
    expect(getNote(n.id)?.title).toBe("Hello");
    expect(updateNote(n.id, { body: "There" })?.body).toBe("There");
    expect(listNotes()).toHaveLength(1);
    expect(deleteNote(n.id)).toBe(true);
    expect(listNotes()).toHaveLength(0);
  });
});
