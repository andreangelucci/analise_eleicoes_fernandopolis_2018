from tqdm import tqdm

# salva em um arquivo separado todos os votos de sao paulo
with open('votos_filtrados_fernandopolis.csv', 'a', encoding='latin1') as f:
    for line in tqdm(open('./bweb_2t_SP_301020181756.csv', 'r', encoding='latin1')):
        if line.split(';')[11].upper() in ['"FERNANDOPOLIS"', '"FERNANDÓPOLIS"']:
            f.write(line)
