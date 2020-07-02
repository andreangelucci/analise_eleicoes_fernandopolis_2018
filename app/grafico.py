''' Parametrização padrão para usar nos marks '''


def customizacao_grafico():
    FONT_NAME = 'IBM Plex Sans,sans-serif,monospace'
    return {
        'config': {
            'view': {
                'width': 'container',
            },
            'mark': {
                'color': 'black',
                'fontSize': 14
            },
            'axisLeft': {
                'labelFont': FONT_NAME,
                'labelFontSize': 14,
            },
        }
    }
