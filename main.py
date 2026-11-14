#!/usr/bin/env python3
"""Penyalin gambar entri lomba food-picture-01.

Foto yang disertakan menampilkan semangkuk ramen tonkotsu dari dekat:
sumpit mengangkat untaian mie menembus uap, telur rebus yang kuningnya
masih lumer, irisan chashu panggang dan taburan daun bawang di atas
kuah yang mengkilap. Skrip ini memeriksa berkasnya lebih dulu, lalu
menyalin isinya tanpa mengubah satu byte pun ke folder keluaran.
Hanya memakai pustaka standar, tanpa dependensi luar.
"""

from hashlib import sha256 as _sidik_jari
from os import environ as _lingkungan
from pathlib import Path as _Jalur
import sys as _sistem

_BATAS_ATAS = 1 << 20
_BATAS_BAWAH = 50_000
_SISI_TERPANJANG = 1024
_NAMA_FOTO = "entry.jpg"
_FOLDER_BOT = "/bot"
_FOLDER_HASIL = "/output"
_NAMA_ENV = "MAKEFUN_OUTPUT_DIR"
_AWAL_JPEG = bytes((0xFF, 0xD8))
_AKHIR_JPEG = bytes((0xFF, 0xD9))
_TANDA_PNG = bytes((0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A))

def _cari_berkas():
    """Menemukan foto entri di samping skrip, di /bot, atau di cwd."""
    _samping = _Jalur(__file__).resolve().parent
    for _calon in (_samping / _NAMA_FOTO, _Jalur(_FOLDER_BOT) / _NAMA_FOTO, _Jalur(_NAMA_FOTO)):
        if _calon.is_file():
            return _calon
    raise FileNotFoundError("tidak menemukan %s di samping skrip, di /bot, atau di direktori kerja" % _NAMA_FOTO)


def _lebar_tinggi(_blob):
    """Mengembalikan (lebar, tinggi) dari kepala PNG atau JPEG."""
    if _blob[:8] == _TANDA_PNG:
        if len(_blob) < 24 or _blob[12:16] != b"IHDR":
            raise ValueError("berkas PNG tanpa potongan IHDR")
        _lebar = int.from_bytes(_blob[16:20], "big")
        _tinggi = int.from_bytes(_blob[20:24], "big")
        return _lebar, _tinggi
    if _blob[:2] == _AWAL_JPEG:
        _pos = 2
        while _pos + 9 < len(_blob):
            if _blob[_pos] != 0xFF:
                raise ValueError("penanda JPEG tidak sejajar")
            _kode = _blob[_pos + 1]
            if _kode in (0xC0, 0xC1, 0xC2):
                _tinggi = int.from_bytes(_blob[_pos + 5:_pos + 7], "big")
                _lebar = int.from_bytes(_blob[_pos + 7:_pos + 9], "big")
                return _lebar, _tinggi
            _loncat = int.from_bytes(_blob[_pos + 2:_pos + 4], "big")
            _pos += 2 + _loncat
        raise ValueError("JPEG tanpa segmen start-of-frame")
    raise ValueError("format tidak dikenal: bukan PNG dan bukan JPEG")

def _jalankan():
    """Memeriksa foto entri lalu menyalinnya utuh ke folder keluaran."""
    _sumber = _cari_berkas()
    _isi = _sumber.read_bytes()
    _jumlah = len(_isi)
    if _jumlah > _BATAS_ATAS:
        raise ValueError("foto melebihi batas 1 MiB: %d byte" % _jumlah)
    if _jumlah < _BATAS_BAWAH:
        raise ValueError("foto di bawah batas kewarasan: %d byte" % _jumlah)
    if _isi[:2] == _AWAL_JPEG and _isi[-2:] != _AKHIR_JPEG:
        raise ValueError("JPEG terpotong: penanda akhir gambar tidak ada")
    _lebar, _tinggi = _lebar_tinggi(_isi)
    if _lebar > _SISI_TERPANJANG or _tinggi > _SISI_TERPANJANG:
        raise ValueError("foto melebihi 1024x1024: %dx%d piksel" % (_lebar, _tinggi))
    _folder = _Jalur(_lingkungan.get(_NAMA_ENV, _FOLDER_HASIL))
    _folder.mkdir(parents=True, exist_ok=True)
    _tujuan = _folder / "entry.png"
    _tujuan.write_bytes(_isi)
    _sidik = _sidik_jari(_isi).hexdigest()
    if _sidik_jari(_tujuan.read_bytes()).hexdigest() != _sidik:
        raise ValueError("salinan di tujuan tidak sama dengan foto asli")
    print("food-picture-01: tersimpan %s (%d byte, %dx%d, sha256 %s)" % (_tujuan, _jumlah, _lebar, _tinggi, _sidik))
    return 0


def _luncur():
    raise SystemExit(_jalankan())


_dijalankan_langsung = __name__ == "__main__"
if _dijalankan_langsung:
    _luncur()



