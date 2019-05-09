# -*- coding: utf-8 -*-
#
# -*- coding: utf-8 -*-
#
# Copyright (C) 2016-2019  SysMedOs_team @ AG Bioanalytik, University of Leipzig:
# SysMedOs_team: Zhixu Ni, Georgia Angelidou, Mike Lange, Maria Fedorova
#
# For more info please contact:
#     Developer Zhixu Ni zhixu.ni@uni-leipzig.de

from epilion.libLION.DefaultParams import abbr_cfg_path
from io import BytesIO
import base64
from flask import send_file

from rdkit import Chem
from rdkit.Chem import Draw
from rdkit.Chem import AllChem, Descriptors, rdMolDescriptors

from epilion.libLION.DefaultParams import logger
from epilion.libLION.LipidNomenclature import ParserFA, ParserPL


def parse_epilion(abbr: str) -> dict:

    fa_decoder = ParserFA()
    pl_decoder = ParserPL()

    info_dct = {}

    if fa_decoder.is_fa(abbr):
        smi = fa_decoder.get_smi_fa(abbr)
        logger.info(abbr + ': ' + smi)
    elif pl_decoder.is_pl(abbr):
        smi = pl_decoder.get_smi_pl(abbr)
        logger.info(abbr + ': ' + smi)
    else:
        logger.info(f'Can NOT parse abbreviation: {abbr}')

    try:
        mol = Chem.MolFromSmiles(smi)
        AllChem.Compute2DCoords(mol)
        # m_mass = Descriptors.MolWt(mol)
        m_exactmass = rdMolDescriptors.CalcExactMolWt(mol)
        m_formula = rdMolDescriptors.CalcMolFormula(mol)
        img = Draw.MolToImage(mol, size=(600, 400))
        img_io = BytesIO()
        img.save(img_io, format='png')
        img_io.seek(0)
        img.save(img_io, format='png')
        img_data = base64.b64encode(img_io.getbuffer())
        img_data_url = r'data:image/png;base64,' + img_data.decode("utf-8")

        info_dct['id'] = abbr
        info_dct['formula'] = m_formula
        info_dct['exactmass'] = '%.4f' % m_exactmass
        info_dct['img'] = img_data_url

    except Exception as e:
        logger.error(f'! FAILED: {abbr}')
        logger.error(f'! FAILED to generate structure from SMILES: {smi}')
        logger.error(e)

    return info_dct