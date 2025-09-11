import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:permission_handler/permission_handler.dart';

class PharmacyFinderPage extends StatefulWidget {
  const PharmacyFinderPage({super.key});

  @override
  State<PharmacyFinderPage> createState() => _PharmacyFinderPageState();
}

class _PharmacyFinderPageState extends State<PharmacyFinderPage>
    with TickerProviderStateMixin {
  late AnimationController _animationController;
  late Animation<double> _fadeAnimation;
  late Animation<Offset> _slideAnimation;

  List<Pharmacy> _pharmacies = [];
  bool _isLoading = false;
  bool _hasPermission = false;
  Position? _currentPosition;
  String _errorMessage = '';

  @override
  void initState() {
    super.initState();
    _setupAnimations();
    _checkLocationPermission();
  }

  void _setupAnimations() {
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 800),
      vsync: this,
    );

    _fadeAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: Curves.easeOut,
    ));

    _slideAnimation = Tween<Offset>(
      begin: const Offset(0, 0.3),
      end: Offset.zero,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: Curves.easeOut,
    ));

    _animationController.forward();
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  Future<void> _checkLocationPermission() async {
    final status = await Permission.location.status;
    if (status.isGranted) {
      setState(() => _hasPermission = true);
      await _getCurrentLocation();
    } else {
      setState(() => _hasPermission = false);
    }
  }

  Future<void> _requestLocationPermission() async {
    final status = await Permission.location.request();
    if (status.isGranted) {
      setState(() => _hasPermission = true);
      await _getCurrentLocation();
    } else {
      setState(() => _hasPermission = false);
      _showPermissionDialog();
    }
  }

  Future<void> _getCurrentLocation() async {
    setState(() => _isLoading = true);
    try {
      final position = await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.high,
      );
      setState(() => _currentPosition = position);
      await _findNearbyPharmacies();
    } catch (e) {
      setState(() => _errorMessage = 'Konum alınamadı: $e');
    } finally {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _findNearbyPharmacies() async {
    if (_currentPosition == null) return;

    setState(() => _isLoading = true);
    try {
      // Simulated pharmacy data - In real app, you'd use a pharmacy API
      final pharmacies = await _getPharmacyData();
      
      // Calculate distances and sort
      for (var pharmacy in pharmacies) {
        pharmacy.distance = _calculateDistance(
          _currentPosition!.latitude,
          _currentPosition!.longitude,
          pharmacy.latitude,
          pharmacy.longitude,
        );
      }
      
      pharmacies.sort((a, b) => a.distance!.compareTo(b.distance!));
      
      setState(() => _pharmacies = pharmacies);
    } catch (e) {
      setState(() => _errorMessage = 'Eczane bilgileri alınamadı: $e');
    } finally {
      setState(() => _isLoading = false);
    }
  }

  double _calculateDistance(double lat1, double lon1, double lat2, double lon2) {
    return Geolocator.distanceBetween(lat1, lon1, lat2, lon2) / 1000; // km
  }

  Future<List<Pharmacy>> _getPharmacyData() async {
    // Simulated data - Replace with real pharmacy API
    await Future.delayed(const Duration(seconds: 1));
    
    return [
      Pharmacy(
        name: 'Merkez Eczanesi',
        address: 'Atatürk Caddesi No: 15, Merkez',
        phone: '0212 555 0123',
        latitude: 41.0082,
        longitude: 28.9784,
        isOnDuty: true,
        workingHours: '08:00 - 22:00',
      ),
      Pharmacy(
        name: 'Sağlık Eczanesi',
        address: 'Cumhuriyet Mahallesi, Sağlık Sokak No: 8',
        phone: '0212 555 0456',
        latitude: 41.0123,
        longitude: 28.9823,
        isOnDuty: false,
        workingHours: '09:00 - 21:00',
      ),
      Pharmacy(
        name: 'Nöbetçi Eczane',
        address: 'İstiklal Caddesi No: 42, Beyoğlu',
        phone: '0212 555 0789',
        latitude: 41.0156,
        longitude: 28.9856,
        isOnDuty: true,
        workingHours: '24 Saat',
      ),
      Pharmacy(
        name: 'Modern Eczane',
        address: 'Bağdat Caddesi No: 156, Kadıköy',
        phone: '0216 555 0321',
        latitude: 40.9876,
        longitude: 29.0234,
        isOnDuty: false,
        workingHours: '08:30 - 20:30',
      ),
      Pharmacy(
        name: 'Hastane Eczanesi',
        address: 'Tıp Fakültesi Yanı, Şişli',
        phone: '0212 555 0654',
        latitude: 41.0456,
        longitude: 28.9876,
        isOnDuty: true,
        workingHours: '07:00 - 23:00',
      ),
    ];
  }

  void _showPermissionDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Konum İzni Gerekli'),
        content: const Text(
          'Yakınlardaki eczaneleri bulabilmek için konum iznine ihtiyacımız var. '
          'Lütfen ayarlardan konum iznini açın.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('İptal'),
          ),
          TextButton(
            onPressed: () {
              Navigator.of(context).pop();
              openAppSettings();
            },
            child: const Text('Ayarlar'),
          ),
        ],
      ),
    );
  }

  Future<void> _callPharmacy(String phone) async {
    final Uri phoneUri = Uri(scheme: 'tel', path: phone);
    if (await canLaunchUrl(phoneUri)) {
      await launchUrl(phoneUri);
    }
  }

  Future<void> _navigateToPharmacy(double lat, double lng) async {
    final Uri mapsUri = Uri.parse(
      'https://www.google.com/maps/dir/?api=1&destination=$lat,$lng',
    );
    if (await canLaunchUrl(mapsUri)) {
      await launchUrl(mapsUri, mode: LaunchMode.externalApplication);
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Yakınlardaki Eczaneler'),
        backgroundColor: theme.colorScheme.primary,
        foregroundColor: theme.colorScheme.onPrimary,
        elevation: 0,
      ),
      body: FadeTransition(
        opacity: _fadeAnimation,
        child: SlideTransition(
          position: _slideAnimation,
          child: Column(
            children: [
              // Header Card
              Container(
                width: double.infinity,
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: [
                      theme.colorScheme.primary,
                      theme.colorScheme.primaryContainer,
                    ],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                ),
                child: Padding(
                  padding: const EdgeInsets.all(20),
                  child: Column(
                    children: [
                      Icon(
                        Icons.local_pharmacy_rounded,
                        size: 48,
                        color: theme.colorScheme.onPrimary,
                      ),
                      const SizedBox(height: 12),
                      Text(
                        'Yakınlardaki Eczaneler',
                        style: theme.textTheme.headlineSmall?.copyWith(
                          color: theme.colorScheme.onPrimary,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        'En yakın eczaneleri bulun ve iletişime geçin',
                        style: theme.textTheme.bodyMedium?.copyWith(
                          color: theme.colorScheme.onPrimary.withOpacity(0.9),
                        ),
                        textAlign: TextAlign.center,
                      ),
                    ],
                  ),
                ),
              ),

              // Content
              Expanded(
                child: _hasPermission
                    ? _buildPharmaciesList()
                    : _buildPermissionRequest(),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildPermissionRequest() {
    final theme = Theme.of(context);
    
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.location_off_rounded,
              size: 64,
              color: theme.colorScheme.primary,
            ),
            const SizedBox(height: 20),
            Text(
              'Konum İzni Gerekli',
              style: theme.textTheme.headlineSmall?.copyWith(
                fontWeight: FontWeight.bold,
                color: theme.colorScheme.primary,
              ),
            ),
            const SizedBox(height: 12),
            Text(
              'Yakınlardaki eczaneleri bulabilmek için konum iznine ihtiyacımız var.',
              style: theme.textTheme.bodyLarge,
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 24),
            SizedBox(
              width: double.infinity,
              height: 48,
              child: FilledButton.icon(
                onPressed: _requestLocationPermission,
                icon: const Icon(Icons.location_on_rounded),
                label: const Text('Konum İznini Aç'),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPharmaciesList() {
    if (_isLoading) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            CircularProgressIndicator(),
            SizedBox(height: 16),
            Text('Eczaneler aranıyor...'),
          ],
        ),
      );
    }

    if (_errorMessage.isNotEmpty) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                Icons.error_outline_rounded,
                size: 64,
                color: Theme.of(context).colorScheme.error,
              ),
              const SizedBox(height: 16),
              Text(
                _errorMessage,
                style: Theme.of(context).textTheme.bodyLarge,
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 16),
              ElevatedButton(
                onPressed: _getCurrentLocation,
                child: const Text('Tekrar Dene'),
              ),
            ],
          ),
        ),
      );
    }

    if (_pharmacies.isEmpty) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.local_pharmacy_outlined,
              size: 64,
              color: Colors.grey,
            ),
            SizedBox(height: 16),
            Text('Yakınlarda eczane bulunamadı'),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: _findNearbyPharmacies,
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: _pharmacies.length,
        itemBuilder: (context, index) {
          final pharmacy = _pharmacies[index];
          return _buildPharmacyCard(pharmacy, index);
        },
      ),
    );
  }

  Widget _buildPharmacyCard(Pharmacy pharmacy, int index) {
    final theme = Theme.of(context);
    
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
      ),
      child: InkWell(
        borderRadius: BorderRadius.circular(16),
        onTap: () => _navigateToPharmacy(pharmacy.latitude, pharmacy.longitude),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header
              Row(
                children: [
                  // Pharmacy icon with status
                  Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: pharmacy.isOnDuty
                          ? Colors.green.shade100
                          : Colors.orange.shade100,
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Icon(
                      Icons.local_pharmacy_rounded,
                      color: pharmacy.isOnDuty ? Colors.green.shade700 : Colors.orange.shade700,
                      size: 24,
                    ),
                  ),
                  const SizedBox(width: 12),
                  
                  // Pharmacy info
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          pharmacy.name,
                          style: theme.textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Row(
                          children: [
                            Icon(
                              Icons.access_time_rounded,
                              size: 16,
                              color: theme.colorScheme.onSurfaceVariant,
                            ),
                            const SizedBox(width: 4),
                            Text(
                              pharmacy.workingHours,
                              style: theme.textTheme.bodySmall?.copyWith(
                                color: theme.colorScheme.onSurfaceVariant,
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                  
                  // Distance badge
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: theme.colorScheme.primaryContainer,
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      '${pharmacy.distance!.toStringAsFixed(1)} km',
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: theme.colorScheme.onPrimaryContainer,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                ],
              ),
              
              const SizedBox(height: 12),
              
              // Address
              Row(
                children: [
                  Icon(
                    Icons.location_on_rounded,
                    size: 16,
                    color: theme.colorScheme.onSurfaceVariant,
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      pharmacy.address,
                      style: theme.textTheme.bodyMedium,
                    ),
                  ),
                ],
              ),
              
              const SizedBox(height: 12),
              
              // Status and actions
              Row(
                children: [
                  // Status indicator
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: pharmacy.isOnDuty
                          ? Colors.green.shade100
                          : Colors.orange.shade100,
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(
                      pharmacy.isOnDuty ? 'Açık' : 'Kapalı',
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: pharmacy.isOnDuty
                            ? Colors.green.shade700
                            : Colors.orange.shade700,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                  
                  const Spacer(),
                  
                  // Action buttons
                  Row(
                    children: [
                      IconButton(
                        onPressed: () => _callPharmacy(pharmacy.phone),
                        icon: const Icon(Icons.phone_rounded),
                        tooltip: 'Ara',
                        style: IconButton.styleFrom(
                          backgroundColor: theme.colorScheme.primaryContainer,
                          foregroundColor: theme.colorScheme.onPrimaryContainer,
                        ),
                      ),
                      const SizedBox(width: 8),
                      IconButton(
                        onPressed: () => _navigateToPharmacy(
                          pharmacy.latitude,
                          pharmacy.longitude,
                        ),
                        icon: const Icon(Icons.directions_rounded),
                        tooltip: 'Yol Tarifi',
                        style: IconButton.styleFrom(
                          backgroundColor: theme.colorScheme.secondaryContainer,
                          foregroundColor: theme.colorScheme.onSecondaryContainer,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class Pharmacy {
  final String name;
  final String address;
  final String phone;
  final double latitude;
  final double longitude;
  final bool isOnDuty;
  final String workingHours;
  double? distance;

  Pharmacy({
    required this.name,
    required this.address,
    required this.phone,
    required this.latitude,
    required this.longitude,
    required this.isOnDuty,
    required this.workingHours,
    this.distance,
  });
}
