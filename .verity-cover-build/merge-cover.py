from zipfile import ZipFile, ZIP_DEFLATED
from pathlib import Path
from copy import deepcopy
from lxml import etree as E
import json, posixpath, re

root=Path(__file__).resolve().parent
source=Path('/private/var/folders/yz/chz0y66d46g01g89dx2l4vrh0000gp/T/codex-file-preview-Dcdnks/Verity_Proposal_Final.pptx')
ns={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
relsns='http://schemas.openxmlformats.org/package/2006/relationships'
ctns='http://schemas.openxmlformats.org/package/2006/content-types'
serialize=lambda v:E.tostring(v,xml_declaration=True,encoding='UTF-8',standalone=True)
with ZipFile(source) as old, ZipFile(root/'cover.pptx') as new:
    originals={n:old.read(n) for n in old.namelist()}
    slide=E.fromstring(new.read('ppt/slides/slide1.xml'))
    relations=E.fromstring(old.read('ppt/slides/_rels/slide1.xml.rels'))
    added={}
    generated_rels=E.fromstring(new.read('ppt/slides/_rels/slide1.xml.rels'))
    for rel in generated_rels:
        if not rel.get('Type','').endswith('/image'):
            continue
        src=posixpath.normpath(posixpath.join('ppt/slides',rel.get('Target'))).lstrip('/')
        dest='ppt/media/verity_fingerprint_cover.png'
        assert dest not in originals
        added[dest]=new.read(src)
        old_id=rel.get('Id')
        new_id='rIdVerityFingerprint'
        E.SubElement(relations,'{'+relsns+'}Relationship',Id=new_id,Type=rel.get('Type'),Target='../media/verity_fingerprint_cover.png')
        for element in slide.iter():
            for attr,val in list(element.attrib.items()):
                if attr.startswith('{'+ns['r']+'}') and val==old_id:
                    element.set(attr,new_id)
    assert len(added)==1
    # Copy only cover visual content; retain original slide metadata and all notes.
    original_slide=E.fromstring(originals['ppt/slides/slide1.xml'])
    original_slide.replace(original_slide.find('p:cSld',ns),deepcopy(slide.find('p:cSld',ns)))
    old_words=re.findall(r'\S+', ' '.join(E.fromstring(originals['ppt/slides/slide1.xml']).xpath('//a:t/text()',namespaces=ns)))
    new_words=re.findall(r'\S+', ' '.join(original_slide.xpath('//a:t/text()',namespaces=ns)))
    from collections import Counter
    assert Counter(old_words)==Counter(new_words), (old_words,new_words)
    changes={'ppt/slides/slide1.xml':serialize(original_slide),'ppt/slides/_rels/slide1.xml.rels':serialize(relations)}
    content_types=E.fromstring(originals['[Content_Types].xml'])
    if not any(x.get('Extension')=='png' for x in content_types):
        E.SubElement(content_types,'{'+ctns+'}Default',Extension='png',ContentType='image/png')
        changes['[Content_Types].xml']=serialize(content_types)
    with ZipFile(root/'candidate.pptx','w',ZIP_DEFLATED) as out:
        for item in old.infolist():
            out.writestr(item,changes.get(item.filename,originals[item.filename]))
        for name,data in added.items():out.writestr(name,data)
    with ZipFile(root/'candidate.pptx') as out:
        changed=[n for n in originals if originals[n]!=out.read(n)]
        assert set(changed)==set(changes)
        untouched=[n for n in originals if n not in changes]
        for n in untouched:assert originals[n]==out.read(n)
        other_slides=[n for n in originals if re.fullmatch(r'ppt/slides/slide\d+\.xml',n) and n!='ppt/slides/slide1.xml']
        assert len(other_slides)==12
        for n in other_slides:assert originals[n]==out.read(n)
        report={'slide_count':13,'changed_parts':changed,'added_parts':list(added),'byte_identical_existing_parts':len(untouched),'all_original_cover_words_preserved':True,'all_other_slides_and_notes_byte_identical':True,'cover_editable_textboxes':len(original_slide.xpath('//p:sp[p:txBody]',namespaces=ns))}
        (root/'preservation-check.json').write_text(json.dumps(report,indent=2))
        print(json.dumps(report,indent=2))
