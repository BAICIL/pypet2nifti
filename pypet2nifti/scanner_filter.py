"""
This is a lazy way to avoid opening a json, simply import this file to extract scanner filter size.
This provides a scanner filter size that is needed to make the final image have a filter size of 8x8x8.
"""
siemens = {
    'HRRT': [6, 6, 6],
    'BioGraph-1080' : [5.5, 5.5, 5.5],
    'HR+': [5, 5, 5],
    'HR': [5.5, 5.5, 3.5],
    'MiE-SCIN-UpgradedHR+': [3.5, 3.5, 3.5],
    'BioGraph-1023-1024': [2, 2, 3],
    'Accel': [2, 2, 3],
    'Exact': [2, 2, 3],
    'Vision': [6.5, 6.5, 6.5],
    'BioGraph-mMR': [5.5, 5.5, 5.5],
    'BioGraph-TruePoint': [5.5, 5.5, 5.5]
}

ge = {
    'GemTF-Old': [5.5, 5.5, 5.5],
    'GemTF-Sharp': [4.5, 4.5, 5],
    'GeminiTF': [4.5, 4.5, 5],
    'IngenuityTF': [4.5, 4.5, 5],
    'Disc690-3DIR': [5.5, 5.5, 5],
    'DiscRX-3DIR': [5.5, 5.5, 5],
    'DiscSTE-3DIR': [5.5, 5.5, 5],
    'Disc690-RP': [5, 5, 3.5],
    'DiscRX-RP': [5, 5, 3.5],
    'DiscSTE-RP': [5, 5, 3.5],
    'DiscLS-FORE-2DIR': [4.5, 4.5, 3],
    'Discovery-MI': [6, 6, 5.5],
    'DiscLS-RP': [5, 5, 2],
    'Advance-FORE-2DIR': [4.5, 4.5, 3],
    'Advance-RP': [5, 5, 2],
    'Signa-PETMR': [5.5, 5.5, 5],
    'DiscST-3DIR': [5, 5, 5],
    'DiscST-FORE-2DIR': [3, 3, 3.5],
    'DiscST-RP': [3,5, 3.5, 3]
}

philips = {
    'Allegro': [3, 3, 3],
    'GemGXL': [3, 3, 3],
    'Gem': [3, 3, 3]
}