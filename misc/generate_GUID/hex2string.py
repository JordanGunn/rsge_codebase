def converter(hex):
    """
    Args:
        hex(str): hexidecimal contract number

    Returns:
        contract_string(str): contract number

    """
    clean_hex = hex.replace('-','')
    contract_string = (bytes.fromhex(clean_hex).decode('utf-8'))
    return contract_string

def main():
    converter()
    
if __name__ == '__main__':
    main()
    
