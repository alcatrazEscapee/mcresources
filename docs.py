from typing import Any, Mapping, Optional, List

from mcresources import *
from mcresources.type_definitions import *

import re
import os
import sys
import logging
import inspect


def main():
    logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(levelname)s : %(message)s')

    makedoc(
        pages=(
            page('ResourceManager.md', ResourceManager),
            page('BlockContext.md', BlockContext),
            page('ItemContext.md', ItemContext),
            page('RecipeContext.md', RecipeContext),
            page('loot_tables.md', loot_tables),
            page('block_states.md', block_states),
            page('advancements.md', advancements),
            page('utils.md', utils),
        ),
        types=(
            typedef('Json', Json),
            typedef('JsonObject', JsonObject),
            typedef('ResourceIdentifier', ResourceIdentifier),
            typedef('T', T),
            typedef('K', K),
            typedef('V', V),
            typedef('DefaultValue', DefaultValue),
            typedef('MapValue', MapValue)
        ),
        link_root='https://github.com/alcatrazEscapee/mcresources/blob/main',
        content_root='../wiki/',
        home_doc="""
    Wiki for `mcresources`, a resource generation library for Minecraft modding. This wiki is generated from the documentation in the mcresources repository
    """.strip()
    )

class PageDoc(NamedTuple):
    title: str
    obj: Any

    def link(self) -> str:
        return self.title.removesuffix('.md')

class TypeDoc(NamedTuple):
    name: str
    type: Any

# Top Level API

def page(title: str, obj: Any) -> PageDoc:
    """ Creates a page for a given object (module or class) """
    return PageDoc(title, obj)

def typedef(name: str, t) -> TypeDoc:
    """ Creates a typedef - a readable name for a composite type (i.e. MyType = Union[str, int, bool]), by defining typedef('MyType', MyType), the shortened name will be used in type annotations """
    return TypeDoc(name, t)

def makedoc(
        pages: Tuple[PageDoc, ...],
        types: Tuple[TypeDoc, ...],
        link_root: str,
        content_root: str,
        home_doc: str
):
    """
    Create and writes a github wiki style documentation for the given content

    - pages is a list of all files that need to be created, see page()
    - types is a list of type definitions used in the documentation, see typedef()
    - link_root is the root github source code link, i.e. `https://github.com/USER/REPO/blob/BRANCH`
    - content_root is the root for where the wiki should be generated, i.e. `../REPO.wiki`
    """
    context = Context(pages, types, link_root)

    doc_pages: List[Tuple[PageDoc, Any]] = []
    for pd in pages:
        context.push_page(pd)

        if inspect.isclass(pd.obj):
            doc_pages.append((pd, class_doc(context, pd.obj)))
        elif inspect.ismodule(pd.obj):
            doc_pages.append((pd, module_doc(context, pd.obj)))
        else:
            logging.warning('Page %s is not a module or a class', pd.title)

    for pd, pd_doc in doc_pages:
        context.push_page(pd)

        lines = pd_doc.apply(context)
        path = os.path.join(content_root, pd.title)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

    # Home page / Table of Contents

    lines = [
        home_doc,
        '',
        '### Contents'
    ]
    for pd, pd_doc in doc_pages:
        lines.append('- [%s](./%s)' % (pd_doc.name, pd.link()))

    path = os.path.join(content_root, 'Home.md')
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))


class Context:

    def __init__(self, pages: Tuple[PageDoc, ...], types: Tuple[TypeDoc, ...], link_root: str):
        self.page = ''
        self.root_type = ''
        self.root = ''
        self.method = ''

        self.link_root = link_root

        self.type_mapping: Mapping[Any, str] = {td.type: td.name for td in types}

        self.pages = {}
        for pd in pages:
            self.pages[pd.obj.__name__] = pd
            self.pages[pd.obj.__name__.split('.')[-1]] = pd

    def push_page(self, pd: PageDoc):
        self.page = pd.title

    def push_root(self, root_type: str, root: str):
        self.root_type = root_type
        self.root = root

    def push_method(self, method: str):
        self.method = method

    def link_src(self, file: str, line: int) -> str:
        path = os.path.relpath(file, os.getcwd())
        path = path.replace('\\', '/')
        return self.link_root + '/' + path + '#L%d' % line

    def link_doc(self, docs: str) -> str:
        for match in re.finditer(r'{@link ([A-Za-z0-9_.#]+)}', docs):
            raw = match.group(1)
            text = '{@link %s}' % raw
            if '#' in raw:
                if not raw.count('#') == 1:
                    logging.warning('Malformed link: %s %s', text, self.info())
                    continue
                obj, field = raw.split('#')
                if obj == '':  # Allow links to the current module
                    obj = self.root
                if obj not in self.pages:
                    logging.warning('Linked object not found: %s %s', obj, self.info())
                    continue
                replace = '[`%s`](./%s#user-content-%s)' % (raw, self.pages[obj].link(), field)
                docs = docs.replace(text, replace)
            else:
                obj = raw
                if obj not in self.pages:
                    logging.warning('Linked object not found: %s %s', obj, self.info())
                    continue
                replace = '[`%s`](./%s)' % (raw, self.pages[obj].title.removesuffix('.md'))
                docs = docs.replace(text, replace)
        return docs

    def info(self) -> str:
        return 'at %s %s.%s() in %s' % (self.root_type, self.root, self.method, self.page)


class ParamDoc(NamedTuple):
    name: str
    type: str
    doc: Optional[str]
    vararg: bool
    kwarg: bool
    default_value: Optional[str]

    def signature(self) -> str:
        var = '**' if self.kwarg else ('*' if self.vararg else '')
        if self.name == 'self' and self.type == 'Any':
            return 'self'
        default = ' = %s' % self.default_value if self.default_value is not None else ''
        return '%s%s: %s%s' % (var, self.name, self.type, default)

class MethodDoc(NamedTuple):
    name: str
    doc: Optional[str]
    args: Tuple[ParamDoc, ...]
    ret: ParamDoc
    file: str
    line: int

    def apply(self, context: Context) -> Sequence[str]:
        context.push_method(self.name)

        lines = []
        if self.doc is not None:
            lines += [context.link_doc(self.doc), '']
        ret = ''
        if self.ret is not None:
            ret = ' -> %s' % self.ret.type
        lines += [
            '```python',
            '%s(%s)%s' % (self.name, self.signature(), ret),
            '```',
            ''
        ]
        anydoc = False
        for arg in self.args:
            if arg.doc is not None:
                anydoc = True
                lines.append('- `%s: %s` %s' % (
                    arg.name,
                    arg.type,
                    arg.doc
                ))
        if self.ret and self.ret.doc:
            lines += ['', '*Returns:* `%s` %s' % (self.ret.type, self.ret.doc)]
        if anydoc:
            lines.append('')
        return lines

    def signature(self) -> str:
        return ', '.join(a.signature() for a in self.args)


class ClassDoc(NamedTuple):
    name: str
    doc: Optional[str]
    ctor: Optional[MethodDoc]
    methods: Tuple[MethodDoc, ...]
    file: str
    line: int

    def apply(self, context: Context) -> Sequence[str]:
        context.push_root('class', self.name)

        lines = []
        if self.doc != '':
            lines += [
                self.doc,
                ''
            ]
        if self.ctor is not None:
            lines += ['<h2 id="__init__"><a href="%s">Constructor</a></h2>' % context.link_src(self.ctor.file, self.ctor.line), '']
            lines += self.ctor.apply(context)

        if self.methods:
            lines += ['## Methods', '']
        for md in self.methods:
            lines += ['<h4 id="%s"><a href="%s"><code>%s</code></a></h4>' % (md.name, context.link_src(md.file, md.line), md.name), '']
            lines += md.apply(context)
        return lines


class ModuleDoc(NamedTuple):
    name: str
    doc: Optional[str]
    methods: Tuple[MethodDoc, ...]
    classes: Tuple[ClassDoc, ...]
    file: str

    def apply(self, context: Context) -> Sequence[str]:
        context.push_root('module', self.name)

        lines = []
        if self.doc is not None:
            lines += [self.doc, '']
        if self.methods:
            lines += ['## Methods', '']
        for md in self.methods:
            lines += ['<h4 id="%s"><a href="%s"><code>%s</code></a></h4>' % (md.name, context.link_src(md.file, md.line), md.name), '']
            lines += md.apply(context)
        return lines


def module_doc(context: Context, obj: Any) -> ModuleDoc:
    methods = tuple(
        method_doc(context, name, method)
        for name, method in obj.__dict__.items()
        if not name.startswith('__') and inspect.isfunction(method)
    )

    obj_doc = None
    if obj.__doc__:
        obj_doc = inspect.cleandoc(obj.__doc__)

    return ModuleDoc(obj.__name__, obj_doc, methods, (), obj.__file__)

def class_doc(context: Context, obj: Any) -> ClassDoc:

    ctor = None
    if obj.__init__:
        ctor = method_doc(context, obj.__name__, obj.__init__)

    methods = tuple(
        method_doc(context, name, method)
        for name, method in obj.__dict__.items()
        if not name.startswith('__')
    )

    obj_doc = ''
    if obj.__doc__:
        obj_doc = inspect.cleandoc(obj.__doc__)

    return ClassDoc(obj.__name__, obj_doc, ctor, methods, inspect.getsourcefile(obj), inspect.getsourcelines(obj)[1])


def method_doc(context: Context, name: str, method: Any) -> MethodDoc:
    context.push_method(name)

    code = method.__code__
    method_body_docs = []
    method_param_docs = {}
    return_param_doc = None
    if method.__doc__:
        for line in [d.strip() for d in inspect.cleandoc(method.__doc__).split('\n')]:
            match = re.match(r'^:param ([A-Za-z0-9_]+): (.*)$', line)
            if match:
                method_param_docs[match.group(1)] = match.group(2)
                continue

            match = re.match(r'^:return: (.*)$', line)
            if match:
                if return_param_doc:
                    logging.warning('Duplicate :return: tag at %s()', name)
                return_param_doc =match.group(1)
                continue

            method_body_docs.append(line)
        method_body_docs = '\n'.join(method_body_docs)
    else:
        method_body_docs = None

    spec = inspect.getfullargspec(method)
    defaults = spec.args[-len(spec.defaults):] if spec.defaults else []
    params = []

    def make_param(param: str):
        param_type = type_annotation(context.type_mapping, spec.annotations[param]) if param in spec.annotations else 'Any'
        param_doc = method_param_docs[param] if param in method_param_docs else None
        param_default = None
        if spec.kwonlydefaults and param in spec.kwonlydefaults:
            param_default = repr(spec.kwonlydefaults[param])
        elif param in defaults:  # spec.defaults is the last n default params
            param_default = repr(spec.defaults[defaults.index(param)])
        pd = ParamDoc(param, param_type, param_doc, param == spec.varargs, param == spec.varkw, param_default)
        params.append(pd)

    for arg in spec.args:
        make_param(arg)

    if spec.varargs is not None:
        make_param(spec.varargs)

    if spec.varkw is not None:
        make_param(spec.varkw)

    for arg in spec.kwonlyargs:
        make_param(arg)

    ret = None
    if 'return' in spec.annotations:
        ret = ParamDoc('return', type_annotation(context.type_mapping, spec.annotations['return']), return_param_doc, False, False, None)

    return MethodDoc(name, method_body_docs, tuple(params), ret, code.co_filename, code.co_firstlineno)


def type_annotation(type_mapping: Mapping[Any, str], raw_type: Any) -> str:
    def recurse(t: Any) -> str:
        if t in type_mapping:
            return type_mapping[t]

        if t is None:
            return 'None'
        if t == int or t == str or t == set or t == dict:
            return t.__name__  # Primitives
        if t.__class__ == type:
            return t.__name__  # Classes
        if t.__class__ == str:
            return t  # Forward Type Reference
        if repr(t) == 'typing.Any':
            return 'Any'

        match = re.match(r'^typing.(Union|Sequence|Dict|List|Tuple|Callable|Optional)\[.*]$', repr(t))
        if match:  # Generic Types
            generic = match.group(1)
            if generic == 'Union':
                return ' | '.join(map(recurse, t.__args__))
            elif generic == 'Dict':
                return 'Dict[%s, %s]' % tuple(map(recurse, list(t.__args__)))
            elif generic == 'Callable':
                return 'Callable[[%s], %s]' % (
                    ', '.join(map(recurse, t.__args__[:-1])),
                    recurse(t.__args__[-1])
                )
            elif generic == 'Optional':
                return '%s | None' % recurse(t.__args__[0])
            elif generic == 'Tuple':
                if not t.__args__:
                    return 'Tuple[]'
                if repr(t.__args__[-1]) == 'Ellipsis':
                    return 'Tuple[%s, ...]' % recurse(t.__args__[0])
                return 'Tuple[%s]' % ', '.join(tuple(map(recurse, list(t.__args__))))
            else:
                return '%s[%s]' % (generic, recurse(t.__args__[0]))

        return 'Any'

    return recurse(raw_type)


if __name__ == '__main__':
    main()
