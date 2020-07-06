import struct


def create_epos_packet(order_json):

    PLU_list = []
    packed_plu = b''
    packed_fast_payment = b''
    packed_custom_products = b''
    packed_custom_messages = b''
    packed_cards = b''



    # Create Order Header
    Order_Header = {}
    Order_Header['sequence'] = order_json['sequence']
    Order_Header['clerkId'] = order_json['clerkId']
    Order_Header['orderType'] = order_json['orderType']
    Order_Header['table'] = order_json['table']
    Order_Header['billNum'] = order_json['billNum']
    Order_Header['covers'] = order_json['covers']
    Order_Header['status'] = order_json['status']
    Order_Header['PrinterMapId'] = order_json['PrinterMapId']
    Order_Header['AutoPriceReceipt'] = order_json['AutoPriceReceipt']
    Order_Header['PrinterNUmber'] = order_json['PrinterNUmber']
    Order_Header['WPDeviceId'] = order_json['WPDeviceId']

    packed_order_header = create_orderHeader(Order_Header)

    #Extract PLU Items - Assuming 0 or more items
    if 'PLUs' in order_json:
        PLUs = order_json['PLUs']
        packed_plu = b''
        for PLU in PLUs:
            packed_plu += create_plu(PLU)

    if 'custom_products' in order_json:
        A = order_json['custom_products']
        packed_custom_products = b''
        for custom_product in A:
            packed_custom_products += create_custom_product(custom_product)

    if 'custom_messages' in order_json:
        A = order_json['custom_messages']
        packed_custom_messages = b''
        for custom_message in A:
            packed_custom_messages += create_custom_message(custom_message)

    if 'cards' in order_json:
        A = order_json['cards']
        packed_cards = b''
        for card in A:
            packed_cards += create_cards(card)

    if 'FastPayment' in order_json:
        # Assuming 0 or 1 item
        FastPayment = order_json['FastPayment']
        packed_fast_payment = create_fast_payment(FastPayment)

    footer = create_order_footer()

    total_len = len(packed_order_header) + len(packed_plu) + \
                len(packed_custom_products) +  len(packed_custom_messages) +  \
                len(packed_cards) + len(packed_fast_payment) + len(footer)

    packet_header = create_packetHeader(12001, 9, total_len)

    packet = packet_header + packed_order_header + packed_plu + packed_custom_products + \
            packed_custom_messages + packed_cards + packed_fast_payment + footer

    dump_bstring(packet)
    print ("")

    return packet



    


def create_packetHeader(lineType, deviceType, dataLen):

    # Packet header
    '''
    Uint8 0 Sync Bytes 1 of 4
    Uint8 255 Sync Bytes 2 of 4
    Uint8 0 Sync Bytes 3 of 4
    Uint8 255 Sync Bytes 4 of 4
    Uint16 LineType* Header Type (see defines below)
    Uint8 64 Internal
    Uint8 64 Internal
    Uint8 0 Internal
    Uint8 DeviceType* Device Type (see defines below)
    Uint16 DataLen Length of data block to follow

    LineTypes
        SVR_NC_DATA 12001 (0x2E 0xE1) Use this for messages you send to POS
        SVR_POS_DATA 12002 (0x2E 0xE2) Expect this for messages you receive from POS
    DeviceType
        DEVICE_EXTERNAL 9
    '''
    return (struct.pack('!BBBBHBBBBH',
        0,
        255,
        0,
        255,
        lineType,
        64,
        64,
        0,
        deviceType,
        dataLen))


def create_orderHeader(Order_Header):

    #Order Header
    '''
    Uint8 01 lineType for a Header Record
    Uint16 18 Block length of header data to follow
    Uint8 Comms Version* Communications Protocol Version Number for Orders
    Uint16 Sequence* Order Sequence Number (0-65000)
    Uint16 Clerk ID ID of clerk placing the order
    Uint8 Order Type The order type (1 = table, 2 = tab)
    Uint16 Table / Tab Number Table / Tab Number
    Uint8 Bill Number Bill Number the order is for (0=default bill, 1+ = bill number)
    Uint16 Covers Number of covers/guests on the table
    Uint8 Status* See defines below (bit flags)
    Uint8 Printer Map ID Printer Map ID to apply (0 = no printer map)
    Uint8 Auto Price Receipt Print a receipt (0 = false, 1 = true)
    Uint16 Printer Number Printer ID to print receipt too, if applicable
    Uint16 WP Device ID WaiterPad Device ID (0-65535)

    Status (bit flags)
        No Status 00000000b
        Reserved 00000001b
        Reserved 00000010b
        Reserved 00000100b
        Print Order To KPs 00001000b
    '''
    CommsVersion = 1

    return (struct.pack('!BHBHHBHBHBBBHH',
            1,
            18,
            CommsVersion,
            Order_Header['sequence'],
            Order_Header['clerkId'],
            Order_Header['orderType'],
            Order_Header['table'],
            Order_Header['billNum'],
            Order_Header['covers'],
            Order_Header['status'],
            Order_Header['PrinterMapId'],
            Order_Header['AutoPriceReceipt'],
            Order_Header['PrinterNUmber'],
            Order_Header['WPDeviceId']))

def create_plu(PLU):
    #PLU Sale
    '''
    Uint8 02 lineType for a PLU Record
    Uint16 * <variable> Block length of the data to follow
    Uint8 Product Class* The product class of the sale (parent / child)
    Uint32 PLU PLU Number (1 - 4,000,000,000)
    Uint8 Quantity Quantity of sale
    Uint8 Price Level Price level of sale
    Uint8 Modifier ID Sale Modifier ID applied to sale (0 = no modifier, 1+ = modifier ID)
    Uint8 Seat Seat Number of sale (if applicable)
    Uint8 Group ID Printing Group override
    Pstring Price Price override (decimal)
    Uint16 Status* See Below (bit flags)
    Uint32 wpIndexNum Unique record identifier for sale. (must be unique for the life of the
    table)

    Product Class: This specifies the type of PLU item. Valid values are as follows. Child PLU types attach to
    parent PLU types.
        1 – Standard Product (parent)
        2 – Side Dish (child)
        4 – Condiment (child)
        5 – Cooking Instruction (child)
        7 – Message PLU (child)

    Status (bit flags)
        Voided Item 00000001b // item is voided
        Chase Item 00000010b // item is chased (not actually ordered)
        Weighed Item 00000100b // needs a weight docket
        Reserved 00001000b // reserved
        Don’t Print 00010000b // don’t print item to KPs
        Price Override 00100000b // has a price override
        Group Override 01000000b // has a group override


    a  = struct.pack("!B%ds" % len(s), len(s), s)
    '''
    blockLength = 1 + 4 + 1 + 1 + 1 + 1 + 1 + 1 + len(PLU['price']) + 2 + 4
    return (struct.pack('!BHBLBBBBB B%ds HL' % (len(PLU['price']),) ,
                2,
                blockLength,
                PLU['productClass'],
                PLU['PLU'],
                PLU['quantity'],
                PLU['priceLevel'],
                PLU['modifierId'],
                PLU['seat'],
                PLU['groupId'],
                len(PLU['price']),
                PLU['price'].encode('utf-8'),
                PLU['status'],
                PLU['wpIndexNum']))

def create_custom_product(custom_product):
    #Custom Product
    '''
    Uint8 03 lineType for a PLU Record
    Uint16 * <variable> Block length of the data to follow
    Uint8 Quantity Quantity of sale
    Uint8 Seat Seat Number of sale (if applicable)
    Uint8 Group ID Printing Group
    Pstring Price Price (decimal)
    Pstring Product Name Name of the Custom Product
    Uint16 Status See Below (bit flags)
    Uint16 KP Printers* KP Printer mask (use bit number for printer number)
    Uint32 wpIndexNum Unique record identifier for sale. (must be unique for the life of the table)

    Status (bit flags)
        Voided Item 00000001b // item is voided
        Chase Item 00000010b // item is chased (not actually ordered)
        Weighed Item 00000100b // needs a weight docket
        Reserved 00001000b // reserved
        Don’t Print 00010000b // don’t print item to KPs
        Reserved 00100000b // reserved
        Reserved 01000000b // reserved
    '''
    blockLength = 1 + 1 + 1 + 1 + len(custom_product['price']) + 1 + len(custom_product['productName']) + 2 + 2 + 4

    return (struct.pack('!BHBBB B%ds B%ds HHL' % (len(custom_product['price']), len(custom_product['productName'])) ,
        3,
        blockLength,
        custom_product['quantity'],
        custom_product['seat'],
        custom_product['groupId'],
        len(custom_product['price']),
        custom_product['price'].encode('utf-8'),
        len(custom_product['productName']),
        custom_product['productName'].encode('utf-8'),
        custom_product['status'],
        custom_product['KpPrinters'],
        custom_product['wpIndexNum']) )

def create_custom_message(custom_message):
    # Custom Message
    '''
    Uint8 04 lineType for a PLU Record
    Uint16 * <variable> Block length of the data to follow
    Uint8 Quantity Quantity of sale
    Uint8 Seat Seat Number of sale (if applicable)
    Pstring Message Text Custom Message Text
    Uint16 Status See Below (bit flags)
    Uint16 KP Printers* KP Printer mask (use bit number for printer number)
    Uint32 wpIndexNum Unique record identifier for sale. (must be unique for the life of the table)

    Status (bit flags)
        Voided Item 00000001b // item is voided
        Chase Item 00000010b // item is chased (not actually ordered)
        Weighed Item 00000100b // needs a weight docket
        Reserved 00001000b // reserved
        Don’t Print 00010000b // don’t print item to KPs
        Reserved 00100000b // reserved
        Reserved 01000000b // reserved

    '''
    blockLength = 1 + 1 + 1 + len(custom_message['MessageText']) + 2 + 2 + 4 
    return (struct.pack('!BHBB B%ds HHL' % len(custom_message['MessageText']),
        4,
        blockLength,
        custom_message['quantity'],
        custom_message['seat'],
        len(custom_message['MessageText']),
        custom_message['MessageText'].encode('utf-8'),
        custom_message['status'],
        custom_message['KpPrinters'],
        custom_message['wpIndexNum']))

def create_card(card):
    # Card
    '''
    Uint8 5 lineType for a card record
    Uint16 … Block length of the data to follow (2 + CardLen)
    Uint8 Card Type Type of card (2 = member card)
    Uint8 Card Len Length of the card string data to follow
    String[CardLen] Card Data Card track data

    Member Card Format
        <six zeros>11<six digit member number><two zeros>
        Card Data Example: 0000001100000200 would represent member 000002
        Card Data Example: 0000001100123400 would represent member 001234
    '''
    blockLength = 1 + 1 + len(cardData)
    return (struct.pack('!BHBBs',
        5,
        blockLength,
        card['cardType'],
        len(card['cardData']),
        card['cardData'].encode('utf-8')) )

def create_fast_payment(fast_payment):
    # Fast Payment
    '''
    Uint8 08 lineType for fastpay payment record
    Uint16 * <variable> Block length of the data to follow
    Uint8 Media Number Media ID that payment is being made with
    Pstring Payment Amount* Amount of the payment (Decimal)
    Pstring Tip Amount* Extra tip amount to be added (if applicable) (decimal)
    Pstring Subtotal* Assumed subtotal of the order (decimal)
    Uint16 Status (bit flag) See below
    Uint8 Printer Num Printer number for receipt (0 = pos default receipt printer)
    '''

    blockLength = 1 + 1 + len(fast_payment['paymentAmount']) + 1 + len(fast_payment['tipAmount']) + 1 + len(fast_payment['subTotal']) + 2 + 1  
    return ( struct.pack('!BHB B%ds B%ds B%ds HB' % (len(fast_payment['paymentAmount']),
                 len(fast_payment['tipAmount']), len(fast_payment['subTotal'])),
        8,
        blockLength,
        fast_payment['mediaId'],
        len(fast_payment['paymentAmount']),
        fast_payment['paymentAmount'].encode('utf-8'),
        len(fast_payment['tipAmount']),
        fast_payment['tipAmount'].encode('utf-8'),
        len(fast_payment['subTotal']),
        fast_payment['subTotal'].encode('utf-8'),
        fast_payment['status'],
        fast_payment['printerNo']) )

def create_order_footer():
    # Order Footer
    '''
    Uint8 15 lineType for the order footer
    Uint16 0 Block length of the data to follow
    '''
    return (struct.pack('!BH',
        15,
        0))




def create_comms_response(responseValue):
    # Comms Status Response
    '''
    Uint8 Response Value Response Value (see below)
    Uint16 0 Reserved
    '''
    return(struct.pack('!IH',
        responseValue,
        0))

def decode_response(response):
    print (response)
    return 1


def dump_bstring(bstring):
    ba = bytearray(bstring)
    hex_string = "".join("%02x " % b for b in ba)
    print (hex_string)








