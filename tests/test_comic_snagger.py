# -*- coding: utf-8 -*-
import comic_snagger.comic_snagger as comic_snagger


def test_main(capfd):
    comic_snagger.main()
    output = capfd.readouterr()[0]
    assert output.strip() == "Successfully installed your project file: comic_snagger"
