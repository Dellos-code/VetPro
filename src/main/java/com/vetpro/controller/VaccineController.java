package com.vetpro.controller;

import com.vetpro.model.Vaccine;
import com.vetpro.service.VaccineService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/vaccines")
public class VaccineController {

    private final VaccineService vaccineService;

    public VaccineController(VaccineService vaccineService) {
        this.vaccineService = vaccineService;
    }

    @PostMapping
    public ResponseEntity<Vaccine> createVaccine(@Valid @RequestBody Vaccine vaccine) {
        Vaccine created = vaccineService.createVaccine(vaccine);
        return ResponseEntity.status(HttpStatus.CREATED).body(created);
    }

    @GetMapping
    public ResponseEntity<List<Vaccine>> getAllVaccines() {
        return ResponseEntity.ok(vaccineService.getAllVaccines());
    }

    @GetMapping("/{id}")
    public ResponseEntity<Vaccine> getVaccine(@PathVariable Long id) {
        return vaccineService.getVaccineById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }
}
