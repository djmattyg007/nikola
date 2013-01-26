# Copyright (c) 2012 Roberto Alsina y otros.

# Permission is hereby granted, free of charge, to any
# person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the
# Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the
# Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice
# shall be included in all copies or substantial portions of
# the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
# PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS
# OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import os

from pygments import highlight
from pygments.lexers import get_lexer_for_filename, TextLexer
from pygments.formatters import HtmlFormatter

from nikola.plugin_categories import Task
from nikola import utils


class Listings(Task):
    """Render pretty listings."""

    name = "render_listings"

    def gen_tasks(self):
        """Render pretty code listings."""
        kw = {
            "default_lang": self.site.config["DEFAULT_LANG"],
            "listings_folder": self.site.config["LISTINGS_FOLDER"],
            "output_folder": self.site.config["OUTPUT_FOLDER"],
        }

        # Things to ignore in listings
        ignored_extensions = (".pyc",)

        def render_listing(in_name, out_name):
            with open(in_name, 'r') as fd:
                try:
                    lexer = get_lexer_for_filename(in_name)
                except:
                    lexer = TextLexer()
                code = highlight(fd.read(), lexer,
                    HtmlFormatter(cssclass='code',
                        linenos="table",
                        nowrap=False,
                        lineanchors=utils.slugify(f),
                        anchorlinenos=True))
            title = os.path.basename(in_name)
            crumbs = out_name.split(os.sep)[1:-1] + [title]
            # TODO: write this in human
            paths = ['/'.join(['..'] * (len(crumbs) - 2 - i)) for i in
                range(len(crumbs[:-2]))] + ['.', '#']
            context = {
                'code': code,
                'title': title,
                'crumbs': zip(paths, crumbs),
                'lang': kw['default_lang'],
                'description': title,
                }
            self.site.render_template('listing.tmpl', out_name.encode('utf8'), context)
        flag = True
        template_deps = self.site.template_system.template_deps('listing.tmpl')
        for root, dirs, files in os.walk(kw['listings_folder']):
            # Render all files
            for f in files:
                ext = os.path.splitext(f)[-1]
                if ext in ignored_extensions:
                    continue
                flag = False
                in_name = os.path.join(root, f)
                out_name = os.path.join(
                    kw['output_folder'],
                    root,
                    f) + '.html'
                yield {
                    'basename': self.name,
                    'name': out_name.encode('utf8'),
                    'file_dep': template_deps + [in_name],
                    'targets': [out_name],
                    'actions': [(render_listing, [in_name, out_name])],
                    # This is necessary to reflect changes in blog title,
                    # sidebar links, etc.
                    'uptodate': [utils.config_changed(
                        self.site.config['GLOBAL_CONTEXT'])],
                    'clean': True,
                }
        if flag:
            yield {
                'basename': self.name,
                'actions': [],
            }
