"""

"""
import pathlib
import itertools
import collections

from xhtml2pdf import pisa
from pycldf.media import MediaTable
from pycldf.cli_util import add_dataset, get_dataset
from clldutils.fonts import charis_font_spec_html
from clldutils.html import HTML, literal
from clldutils.misc import data_url

from pytsammalex.gbif import GBIF, RANKS


def register(parser):
    add_dataset(parser)
    parser.add_argument('language')


def run(args):
    gbif = GBIF()
    ds = get_dataset(args)
    media = MediaTable(ds)
    media_by_taxon = collections.defaultdict(list)
    media_by_id = {}
    for f in media:
        media_by_taxon[f.row['Taxon_ID']].append(f)
        media_by_id[f.id] = f
    taxa = sorted(
        ds['ParameterTable'],
        key=lambda r: tuple([r[k] or '' for k in
                             'kingdom phylum class_ order family genus'.split()] + [RANKS.index(r['rank'])]))
    names = collections.defaultdict(list)
    for row in ds['FormTable']:
        if row['Language_ID'] == args.language:
            names[row['Parameter_ID']].append(row)
    taxa = [t for t in taxa if t['ID'] in names]
    paragraphs = []

    def link_callback(src_attr, *args):
        if src_attr in media_by_id:
            f = media_by_id[src_attr]
            return data_url(f.read(), mimetype=f.mimetype.string)
        return src_attr

    def taxon_item(taxon):
        try:
            vnames = gbif.get_vernacular_names(taxon['GBIF_ID'])
        except:
            vnames = {}
        content = [HTML.h6(HTML.a(
            '{} {}'.format(taxon['rank'], taxon['Name']),
            href=ds['ParameterTable', 'gbifReference'].valueUrl.expand(taxon)))]

        img = ''
        if media_by_taxon[taxon['ID']]:
            img = HTML.img(class_='image', src=media_by_taxon[taxon['ID']][0].id)
        names_html = []
        if vnames:
            for tag, name in vnames.items():
                names_html.extend([HTML.dt(tag), HTML.dd(name)])
        names_html.extend([HTML.dt(args.language), HTML.dd('; '.join(r['Form'] for r in names[taxon['ID']]))])
        content.append(HTML.table(HTML.tr(
            HTML.td(HTML.dl(*names_html)),
            HTML.td(img)
        )))
        return HTML.div(*content)

    for kingdom, i in itertools.groupby(taxa, lambda r: r['kingdom']):
        if not kingdom:
            continue
        i = list(i)
        paragraphs.append(HTML.h2('Kingdom ' + kingdom))
        while i and i[0]['rank'] == 'KINGDOM':
            ii = i.pop(0)
            print(ii['Name'])

        for phylum, j in itertools.groupby(i, lambda r: r['phylum']):
            if not phylum:
                continue

            j = list(j)
            paragraphs.append(HTML.h3('Phylum ' + phylum))
            while j and j[0]['rank'] == 'PHYLUM':
                ii = j.pop(0)
                print(ii['Name'])

            for class_, k in itertools.groupby(j, lambda r: r['class_']):
                k = list(k)
                paragraphs.append(HTML.h4('Class ' + class_))
                while k and k[0]['rank'] == 'KINGDOM':
                    ii = k.pop(0)
                    print(ii['Name'])

                for order, l in itertools.groupby(k, lambda r: r['order']):
                    l = list(l)
                    paragraphs.append(HTML.h5('Order ' + order))
                    while l and l[0]['rank'] == 'K':
                        ii = l.pop(0)
                        print(ii['Name'])

                    for family, m in itertools.groupby(l, lambda r: r['family']):
                        m = list(m)
                        paragraphs.append(HTML.h5('Family ' + family))
                        while m and m[0]['rank'] == 'FAMILY':
                            ii = m.pop(0)
                            print(ii['Name'])

                        for genus, n in itertools.groupby(m, lambda r: r['genus']):
                            n = list(n)
                            paragraphs.append(HTML.h5('Genus ' + genus))
                            while n and n[0]['rank'] == 'GENUS':
                                ii = n.pop(0)
                                print(ii['Name'])

                            paragraphs.append(HTML.ul(
                                *[HTML.li(taxon_item(ii)) for x, ii in enumerate(n)]
                            ))
    with pathlib.Path('fg.pdf').open('wb') as fp:
        title_page = literal("""
    <div id="header_content" style="text-align: center;"> --title-- </div>

    <div id="footer_content" style="text-align: center;"><pdf:pagenumber>
     of <pdf:pagecount>
     </div>
    
    <pdf:nexttemplate name="title_template" />
    <p>&nbsp;<p>
    <p>&nbsp;<p>
    <p>&nbsp;<p>
    <p>&nbsp;<p>
    <div class="title">
    <h1 style="text-align: center; font-size: 12mm;">{} names for Plants and Animals</h1>
<!--h2 style="text-align: center; font-size: 8mm;">%(editors)s</h2>
<p style="font-size: 5mm;">
This document was created from <a href="%(url)s">%(dataset)s</a> on %(date)s.
</p>
<p style="font-size: 5mm;">
%(dataset)s is published under a %(license)s and should be cited as
</p>
<blockquote style="font-size: 5mm;"><i>%(citation)s</i></blockquote>
<p style="font-size: 5mm;">
A full list of contributors is available at
<a href="%(url)scontributors">%(url)scontributors</a>
</p>
<p style="font-size: 5mm;">
The list of references cited in this document is available at
<a href="%(url)ssources">%(url)ssources</a>
</p-->
    </div>
    <pdf:nexttemplate name="regular_template" />
    <pdf:nextpage />
        """.format(args.language))
        style = HTML.style(literal("""
    html,body {
        font-family: 'charissil'; font-size: 3.5mm;
    }
    @page title_template { margin-top: 5cm; }
    @page regular_template {
        size: a4 portrait;
        @frame header_frame {           /* Static Frame */
            -pdf-frame-content: header_content;
            left: 40pt; width: 532pt; top: 40pt; height: 30pt;
        }
        @frame content_frame {          /* Content Frame */
            left: 40pt; width: 532pt; top: 80pt; height: 652pt;
        }
        @frame footer_frame {           /* Another static Frame */
            -pdf-frame-content: footer_content;
            left: 40pt; width: 532pt; top: 782pt; height: 20pt;
        }
    }
    div.title { margin-bottom: 5cm; }
    h1 { font-size: 30mm; text-align: center; }
    h2 { -pdf-keep-with-next: true; padding-bottom: -2mm; }
    h3 { -pdf-keep-with-next: true; padding-bottom: -2mm; }
    p { -pdf-keep-with-next: true; }
    p.separator { -pdf-keep-with-next: false; font-size: 1mm; }
    img.image { zoom: 55%; border: 1px solid black; }
    td { text-align: center; }"""))
        pisa.CreatePDF(
            str(HTML.html(
                HTML.head(charis_font_spec_html(), style),
                HTML.body(title_page, *paragraphs))),
            dest=fp,
            link_callback=link_callback,
        )


def vs():
    """
<%def name="td_image(image)">
    % if image:
        <% license = u.license_name(image.get_data('permission') or '') %>
        <td width="33%"><br/>
            <img class="image" src="${image.jsondata.get('web')}" />&nbsp;
            <br/>
                <span style="font-size: 2.5mm;">
                    ${license}
                    ${'&copy;' if license != 'Public Domain' else 'by'|n}
                    ${image.get_data('creator') or ''}
                </span>
        </td>
    % endif
</%def>
<p style="padding-bottom: -2mm;">
<strong><i><a href="${request.resource_url(ctx.parameter)}">${ctx.parameter.name}</a></i></strong>
% if ctx.parameter.description:
<span style="color: #666;">${ctx.parameter.description}</span>
% endif
${u.names_in_2nd_languages(ctx)|n}.
% if ctx.parameter.characteristics:
    <span>Characteristics: ${ctx.parameter.characteristics}.</span>
% endif
% if ctx.parameter.biotope:
    <span>Biotope: ${ctx.parameter.biotope}.</span>
% endif
% if ctx.parameter.references:
    <span>(${ctx.parameter.formatted_refs(request)|n})</span>
% endif
</p>
<ul style="padding-top: -1mm;">
% for name in ctx.values:
    <li>
    <strong>${name.name}</strong>
    % if name.ipa:
    [${name.ipa}]
    % endif
.
% if name.grammatical_info:
<i>${name.grammatical_info}</i>.
% endif
% if name.meaning:
"${name.meaning}".
% endif
% if name.literal_translation:
Lit. "${name.literal_translation}".
% endif
% if name.usage:
[name.usage].
% endif
% if name.plural_form:
Plural <i>${name.plural_form}</i>.
% endif
% if name.source_language:
From ${name.source_language}
% if name.source_form:
<i>${name.source_form}</i>
% endif
.
% endif
% if name.linguistic_notes:
${name.linguistic_notes}.
% endif
% if name.related_lexemes:
Related words: ${name.related_lexemes}.
% endif
% if name.categories:
Categories: <i>${', '.join(use.name for use in name.categories)}</i>.
% endif
% if name.habitats:
Habitats: <i>${', '.join(use.name for use in name.habitats)}</i>.
% endif
% if name.introduced:
${name.introduced}.
% endif
% if name.uses:
Uses: ${', '.join(use.name for use in name.uses)}.
% endif
% if name.importance:
${name.importance}.
% endif
% if name.associations:
${name.associations}.
% endif
% if name.ethnobiological_notes:
${name.ethnobiological_notes}.
% endif
    </li>
% endfor
</ul>
% if ctx.parameter._files:
    <table width="100%" style="padding-top: -2mm;"><tr>
    % if 'thumbnail' in ''.join(f.name or '' for f in ctx.parameter._files):
        % for tag in ['thumbnail' + str(j + 1) for j in range(3)]:
            ${td_image(ctx.parameter.image(tag=tag))}
        % endfor
    % else:
        % for i in range(3):
            ${td_image(ctx.parameter.image(index=1))}
        % endfor
    % endif
    </tr></table>
% endif
    """
