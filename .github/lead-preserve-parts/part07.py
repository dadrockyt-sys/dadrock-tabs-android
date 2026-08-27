    text += '\n'.join(lines)
cp.write_text(text,encoding='utf-8')

assert marker in cp.read_text(encoding='utf-8')
assert 'Reference-facing score calls this continuation: **0**.' in cp.read_text(encoding='utf-8')
assert provenance['machineReadableReference']['gitBlobSha']==blob
assert provenance['safety']['mainOrProductionModified'] is False
print(json.dumps({'reference':str(ref_path),'receipt':str(receipt_path),'provenance':str(prov_path),'sha256':sha,'gitBlobSha':blob,'audit':ref['audit'],'currentRenderedSetSha256':current_set_sha},indent=2))
