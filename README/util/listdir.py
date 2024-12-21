#!/usr/bin/env python

import argparse
import os
import os.path

def get_argparser():
  parser = argparse.ArgumentParser()
  parser.add_argument("--directory_path", type=str, default=None,
                      help="directory path (default: None)")
  parser.add_argument("--file_limit", type=int, default=1,
                      help="file limit (default: 1)")
  return parser

def parse_dir(dir_path, file_lim):
  tree = {}
  root = True
  for (dp, dn, fn) in os.walk(dir_path):
    subpaths = dp.split("/")
    if root:
      reference_indent_level = len(subpaths)
      root = False

    children = {
      "name": subpaths[-1],
      "path": dp,
      "indent_level": len(subpaths),
      "dirs": dn,
      "files": fn[:file_lim],
      "overflow": True if len(fn) > file_lim else False
    }
    tree[dp] = children
  for dp in tree:
    tree[dp]["indent_level"] -= reference_indent_level
  return tree

def convert_tree_to_block(tree):
  seen = set()
  block = "```\n"
  def append_files(files, overflow, indent_level, extra_padding=False):
    nonlocal block
    indent_level = (" " * 4) * ((indent_level + 1) if extra_padding else indent_level)
    for fn in files:
      block += f"{indent_level}{fn}\n"
    if overflow:
      block += f"{indent_level}...\n"

  def recursive_build(tree, min_indent_level):
    nonlocal block, seen
    for dp in tree:
      if dp not in seen:
        indent_level = tree[dp]["indent_level"]
        if indent_level < min_indent_level:
          break
        indent = (" " * 4) * indent_level
        block += f"{indent}/{tree[dp]['name']}\n"
        seen.add(dp)
        recursive_build(tree, indent_level)
        files, overflow = tree[dp]["files"], tree[dp]["overflow"]
        append_files(files, overflow, indent_level)

  for dp in tree:
    indent_level = tree[dp]["indent_level"]
    indent = (" " * 4) * indent_level
    block += f"{indent}/{tree[dp]['name']}\n"
    seen.add(tree[dp]["path"])
    recursive_build(tree, indent_level)
    files, overflow = tree[dp]["files"], tree[dp]["overflow"]
    append_files(files, overflow, indent_level, extra_padding=True)
    break
  block += "```"
  return block

def main():
  opts = get_argparser().parse_args()
  assert (opts.directory_path is not None and os.path.isdir(opts.directory_path))
  assert (opts.file_limit > 0)

  tree = parse_dir(opts.directory_path, opts.file_limit)
  block = convert_tree_to_block(tree)
  print(block)

if __name__ == "__main__":
  main()
