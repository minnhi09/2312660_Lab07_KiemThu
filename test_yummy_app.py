import unittest
from unittest.mock import patch

import gps_service
from yummy_app import YummyApp


class TestEasyLevel(unittest.TestCase):
    """Kiem thu chuc nang co ban tinh tien don hang."""

    def setUp(self):
        self.app = YummyApp()

    def test_calculate_total_for_single_item(self):
        cart = {"pho": 2}
        self.assertEqual(self.app.calculate_order_total(cart), 100000)

    def test_calculate_total_for_multiple_items(self):
        cart = {"pho": 1, "bun": 1}
        self.assertEqual(self.app.calculate_order_total(cart), 95000)

    def test_calculate_total_for_empty_cart(self):
        self.assertEqual(self.app.calculate_order_total({}), 0.0)

    def test_calculate_total_with_zero_quantity(self):
        cart = {"pho": 0}
        self.assertEqual(self.app.calculate_order_total(cart), 0.0)


class TestMediumLevel(unittest.TestCase):
    """Kiem thu ma khuyen mai theo trang thai mang va phien ban HDH."""

    def test_apply_promo_code_online_valid(self):
        app = YummyApp(network_status="online")
        self.assertEqual(app.apply_promo_code(100000, "GIAM10"), 90000)

    def test_apply_promo_code_offline(self):
        app = YummyApp(network_status="offline")
        with self.assertRaises(ConnectionError):
            app.apply_promo_code(100000, "GIAM10")

    def test_apply_new_os_promo_on_os_15(self):
        app = YummyApp(os_version=15)
        self.assertEqual(app.apply_promo_code(100000, "NEW_OS_ONLY"), 80000)

    def test_apply_new_os_promo_on_os_14(self):
        app = YummyApp(os_version=14)
        with self.assertRaises(ValueError):
            app.apply_promo_code(100000, "NEW_OS_ONLY")


class TestHardLevel(unittest.TestCase):
    """Kiem thu de xuat nha hang khi gia lap dich vu GPS."""

    def setUp(self):
        self.app = YummyApp()

    @patch("yummy_app.gps_service.get_current_location")
    def test_get_nearby_restaurants_inside_service_area(self, mock_location):
        mock_location.return_value = (10.0, 105.0)
        self.assertEqual(
            self.app.get_nearby_restaurants(),
            ["Nha hang Pho Ly Quoc Su", "Bun cha Huong Lien"],
        )
        mock_location.assert_called_once_with()

    @patch("yummy_app.gps_service.get_current_location")
    def test_get_nearby_restaurants_outside_service_area(self, mock_location):
        mock_location.return_value = (20.0, 110.0)
        self.assertEqual(self.app.get_nearby_restaurants(), [])
        mock_location.assert_called_once_with()

    @patch("yummy_app.gps_service.get_current_location")
    def test_get_nearby_restaurants_when_gps_signal_lost(self, mock_location):
        mock_location.side_effect = gps_service.GPSSignalLostError()
        self.assertEqual(
            self.app.get_nearby_restaurants(), "Khong the xac dinh vi tri."
        )
        mock_location.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
