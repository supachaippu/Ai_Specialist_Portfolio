
// ====================================================
// โค้ดนี้ถูกสร้างอัตโนมัติจากไฟล์ build_concert.py
// ====================================================

const concertDetails = {
    "extra_chair_price": 200,
    "lock_table_price": 500,
    "ticket_price_vvip_2": 0,
    "ticket_price_vvip_4": 4000,
    "ticket_price_vvip_6": 6000,
    "ticket_price_vip_2": 0,
    "ticket_price_vip_4": 3000,
    "ticket_price_vip_6": 4500,
    "ticket_price_normal_2": 0,
    "ticket_price_normal_4": 2000,
    "ticket_price_normal_6": 3000,
    "ticket_price_small_2": 1000,
    "ticket_price_small_4": 0,
    "ticket_price_small_6": 0,
    "privilege_vvip": "โซฟาติดขอบเวทีสุดเอ็กซ์คลูซีฟ",
    "privilege_vip": "มองเห็นเวทีชัดเจน นั่งสบาย",
    "privilege_normal": "โต๊ะนั่งชิลๆ วิวดี",
    "privilege_small": "โต๊ะยืนสายปาร์ตี้มันส์ๆ"
};

const allTables = {
    "1": [
        {
            "id": "1",
            "table_number": "VVIP1",
            "table_type": "VVIP",
            "capacity": 6,
            "x_position": 40,
            "y_position": 18,
            "is_available": true,
            "allow_extra_chairs": true,
            "max_extra_chairs": 2
        },
        {
            "id": "2",
            "table_number": "VVIP2",
            "table_type": "VVIP",
            "capacity": 6,
            "x_position": 50,
            "y_position": 18,
            "is_available": true,
            "allow_extra_chairs": true,
            "max_extra_chairs": 2
        },
        {
            "id": "3",
            "table_number": "VVIP3",
            "table_type": "VVIP",
            "capacity": 6,
            "x_position": 60,
            "y_position": 18,
            "is_available": true,
            "allow_extra_chairs": true,
            "max_extra_chairs": 2
        },
        {
            "id": "4",
            "table_number": "VIP1",
            "table_type": "VIP",
            "capacity": 4,
            "x_position": 30,
            "y_position": 30,
            "is_available": true,
            "allow_extra_chairs": true,
            "max_extra_chairs": 1
        },
        {
            "id": "5",
            "table_number": "VIP2",
            "table_type": "VIP",
            "capacity": 4,
            "x_position": 45,
            "y_position": 30,
            "is_available": true,
            "allow_extra_chairs": true,
            "max_extra_chairs": 1
        },
        {
            "id": "6",
            "table_number": "VIP3",
            "table_type": "VIP",
            "capacity": 4,
            "x_position": 60,
            "y_position": 30,
            "is_available": true,
            "allow_extra_chairs": true,
            "max_extra_chairs": 1
        },
        {
            "id": "7",
            "table_number": "N1",
            "table_type": "Normal",
            "capacity": 4,
            "x_position": 20,
            "y_position": 45,
            "is_available": true,
            "allow_extra_chairs": false,
            "max_extra_chairs": 0
        },
        {
            "id": "8",
            "table_number": "N2",
            "table_type": "Normal",
            "capacity": 4,
            "x_position": 35,
            "y_position": 45,
            "is_available": true,
            "allow_extra_chairs": false,
            "max_extra_chairs": 0
        },
        {
            "id": "9",
            "table_number": "N3",
            "table_type": "Normal",
            "capacity": 4,
            "x_position": 50,
            "y_position": 45,
            "is_available": true,
            "allow_extra_chairs": false,
            "max_extra_chairs": 0
        },
        {
            "id": "10",
            "table_number": "N4",
            "table_type": "Normal",
            "capacity": 4,
            "x_position": 65,
            "y_position": 45,
            "is_available": true,
            "allow_extra_chairs": false,
            "max_extra_chairs": 0
        }
    ],
    "2": [
        {
            "id": "11",
            "table_number": "S1",
            "table_type": "Small",
            "capacity": 2,
            "x_position": 30,
            "y_position": 20,
            "is_available": true,
            "allow_extra_chairs": false,
            "max_extra_chairs": 0
        },
        {
            "id": "12",
            "table_number": "S2",
            "table_type": "Small",
            "capacity": 2,
            "x_position": 50,
            "y_position": 20,
            "is_available": true,
            "allow_extra_chairs": false,
            "max_extra_chairs": 0
        },
        {
            "id": "13",
            "table_number": "S3",
            "table_type": "Small",
            "capacity": 2,
            "x_position": 70,
            "y_position": 20,
            "is_available": true,
            "allow_extra_chairs": false,
            "max_extra_chairs": 0
        }
    ]
};
