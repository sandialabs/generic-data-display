meta:
  id: basic_image_kaitai
  title: BASIC IMAGE
  endian: be
  encoding: utf-8
doc: |
  This is a basic variable sized image.
  The image size is defined by the row/col size
  The actual number of bytes for the image is defined by the byte_size
seq:
  - id: row
    type: s4
  - id: col
    type: s4
  - id: byte_size
    type: s4
  - id: bytes_per_pixel
    type: s4
  - id: image_id
    type: s4
  - id: date_len
    type: s4
  - id: date
    type: str
    size: date_len
    encoding: UTF-8
  - id: image
    size: row * col * bytes_per_pixel