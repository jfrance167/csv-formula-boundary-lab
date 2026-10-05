# Decisions — October 5, 2026

- Original bounded stdlib comparison instead of adopting Papa Parse/defusedcsv:
  their broader mitigation/configuration contracts do not match this demonstration.
- Exact concrete built-in containers/strings avoid arbitrary iterator/coercion
  behavior. Unpaired surrogate codepoints rejected without silent replacement.
- No headers inferred. All rows are ordinary data, and every cell changes under
  apostrophe-all, even empty/already-prefixed values. Non-idempotence is explicit.
- Indicators are frozen conservative rules; do not normalize/trim text or exempt
  numeric-looking values by locale. Consumer interpretation always unverified.
- Strict JSON has preparse byte/depth limits, bounded numeric callbacks and duplicate/
  unknown/type rejection. Fixed dialect; no arbitrary CSV importer or sniffing.
- Independent exact serialization/coordinate tests supplement roundtrips, because
  a writer/reader pair can share a mistake. Two focused mutations validate detection.
- CLI reuses reviewed local failure behavior. Partial failed writes are possible;
  output limits and nonzero exits are honest, with no atomic-output promise.
- Prepared pinned security CI locally. No hosted execution/publication implied.
