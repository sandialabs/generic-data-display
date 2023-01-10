meta:
  id: basic_kaitai
  title: BASIC FORMAT
  endian: be
  encoding: utf-8
doc: |
  This is our coooool basic format
seq:
  - id: counter
    type: s4
  - id: date_len
    type: s4
  - id: date
    type: str
    size: date_len
    encoding: UTF-8