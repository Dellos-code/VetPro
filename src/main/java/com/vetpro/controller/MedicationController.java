package com.vetpro.controller;

import com.vetpro.model.Medication;
import com.vetpro.service.MedicationService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/medications")
public class MedicationController {

    private final MedicationService medicationService;

    public MedicationController(MedicationService medicationService) {
        this.medicationService = medicationService;
    }

    @PostMapping
    public ResponseEntity<Medication> addMedication(@Valid @RequestBody Medication medication) {
        Medication created = medicationService.addMedication(medication);
        return ResponseEntity.status(HttpStatus.CREATED).body(created);
    }

    @GetMapping
    public ResponseEntity<List<Medication>> getAllMedications() {
        return ResponseEntity.ok(medicationService.getAllMedications());
    }

    @GetMapping("/{id}")
    public ResponseEntity<Medication> getMedication(@PathVariable Long id) {
        return medicationService.getMedicationById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @PutMapping("/{id}")
    public ResponseEntity<Medication> updateMedication(@PathVariable Long id,
                                                       @Valid @RequestBody Medication medication) {
        return medicationService.getMedicationById(id)
                .map(existing -> ResponseEntity.ok(medicationService.updateMedication(id, medication)))
                .orElse(ResponseEntity.notFound().build());
    }

    @PutMapping("/{id}/stock")
    public ResponseEntity<Medication> updateStock(@PathVariable Long id,
                                                  @RequestParam Integer quantity) {
        return ResponseEntity.ok(medicationService.updateStock(id, quantity));
    }

    @GetMapping("/low-stock")
    public ResponseEntity<List<Medication>> getLowStock() {
        return ResponseEntity.ok(medicationService.getLowStockMedications());
    }
}
